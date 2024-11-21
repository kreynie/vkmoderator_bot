from asyncio import sleep as asleep
from time import localtime, strftime
from typing import TypeAlias

from vkbottle import VKAPIError
from vkbottle.user import Message
from vkbottle_types.objects import PhotosPhoto

import src.helpfuncs.list_stuffs_utils
from src.blueprints import rules
from src.helpfuncs import functions as funcs, vkfunctions as vkf
from src.schemas import Stuff
from src.schemas.object_validators import BannerInfo
from src.schemas.registration import BanRegistrationInfo
from src.schemas.user import UserSchema
from src.services.stuffs import StuffsService
from src.utils.dependencies import UOWDep
from src.utils.unitofwork import IUnitOfWork
from .base_labeler import labeler
from config import logger

ReturnResult: TypeAlias = tuple[str | None, str | None]


@labeler.private_message(
    access=[rules.StuffGroups.MODERATOR, rules.Rights.LOW],
    text=funcs.split_for_text_for_command("Бан <user> <comment> <ban_time>"),
)
async def ban_user_in_group(
    message: Message,
    user: str = "",
    comment: str = "",
    ban_time: str = "",
) -> None:
    help_text_required = 'Воспользуйся командой "Помощь" для справки'
    if not user:
        return await message.answer(f"Нет нарушителя.\n{help_text_required}")

    if not comment:
        return await message.answer(f"Забыл причину бана.\n{help_text_required}")

    try:
        user_info = await vkf.get_user_info(user)
    except VKAPIError as e:
        logger.error(e)
        return await message.answer("❌ Не удалось получить информацию о пользователе\n"
                                    f"Ошибка на стороне VK (код {e.code}):{e.error_msg}")
    except Exception as e:
        logger.error(e)
        return await message.answer("❌ Не удалось получить информацию о пользователе\n"
                                    "Произошла непредвиденная ошибка")

    already_banned = await vkf.check_if_banned(user_info.id)
    if already_banned:
        return await message.answer("Пользователь уже забанен в группе")

    photo_attachments = message.get_photo_attachments()
    ban_result, return_reason = await perform_ban(
        banner_vk_id=message.from_id,
        user_info=user_info,
        ban_time=ban_time,
        comment=comment.lower(),
        attachments=photo_attachments,
    )

    if return_reason is not None:
        return await message.answer(
            f"⚠️Произошла ошибка во время попытки оформления бана\n{return_reason}"
        )

    await message.answer(ban_result)
    await asleep(3)


async def perform_ban(
    banner_vk_id: int,
    user_info: UserSchema,
    ban_time: str,
    comment: str,
    attachments: list[PhotosPhoto],
) -> ReturnResult:
    full_comment = funcs.get_reformatted_comment(comment)
    ban_time_text = funcs.time_to_text(ban_time)

    if full_comment is None:
        return None, 'Проверь ПРИЧИНУ бана (команда "сокращения")'

    if ban_time_text is None:
        return None, "Проверь ВРЕМЯ бана"

    is_post_needed = ban_time_text not in ("час", "сутки", "день") or comment == "ода"
    if is_post_needed and not attachments:
        return None, "Проверь картинки для бани"

    try:
        banner = await get_banner_info(banner_vk_id)
    except Exception as e:
        logger.error(e)
        return None, "❌ Не удалось получить информацию о баннере (модераторе) для поста"

    time_unix = funcs.calculate_unix_time_after_period(ban_time)

    end_time_text = "навсегда"
    if time_unix is not None:
        end_time_text = (
            f"Болеть будет до {strftime('%d.%m.%y %H:%M', localtime(time_unix))}"
        )

    post_info = ""
    post_error_occurred = False
    if is_post_needed:
        ban_info = BanRegistrationInfo(
            banner_info=banner,
            user_info=user_info,
            comment=comment,
            ban_time=ban_time_text,
        )
        post_error_occurred, post_info = await post(ban_info, attachments)

    if is_post_needed and post_error_occurred:
        return None, post_info

    result = await vkf.ban(
        owner_id=user_info.id,
        end_date=time_unix,
        reason=0,
        comment=f"{full_comment} | {banner.key}",
        comment_visible=True,
    )

    if result != 1:
        return None, "Не удалось забанить человека на стороне VK"

    return (
        f"{user_info.full_name} получил банхаммером\n{end_time_text}\n\n{post_info}",
        None,
    )


async def get_banner_info(user_vk_id: int, uow: IUnitOfWork = UOWDep) -> BannerInfo:
    banner: Stuff = await StuffsService().get_stuff_by(
        uow, user_id=user_vk_id, group_id=rules.StuffGroups.MODERATOR.value
    )
    prefix = src.helpfuncs.list_stuffs_utils.get_stuff_prefix(banner.allowance, "МВ")
    banner_key = prefix + str(banner.key)
    return BannerInfo(moderator=banner, key=banner_key)


async def post(
    ban_info: BanRegistrationInfo,
    photos: list,
) -> tuple[bool, str]:
    try:
        uploaded_photos = await vkf.upload_images(photos)
    except VKAPIError as e:
        logger.error(e)
        return True, (
            "❌ Не удалось загрузить фото\n"
            f"Ошибка на стороне ВК (код {e.code}):{e.error_msg}"
        )
    except Exception as e:
        logger.error(e)
        return True, "❌ Не удалось загрузить фото для бани. Попробуй повторить"
    post_text = (
        f"{ban_info.user_info.full_name}",
        f"https://vk.com/id{ban_info.user_info.id}",
        f"{ban_info.comment} - {ban_info.ban_time}",
        f"@id{ban_info.banner_info.moderator.user_id}({ban_info.banner_info.key})",
    )

    try:
        await vkf.post(
            from_group=True,
            message="\n".join(post_text),
            attachments=uploaded_photos,
        )
    except VKAPIError as e:
        logger.error(e)
        return True, (
            "❌ Не удалось сделать пост в бане\n"
            f"Ошибка на стороне ВК (код {e.code}):{e.error_msg}"
        )
    except Exception as e:
        logger.error(e)
        return True, "❌ Не удалось сделать пост в бане по непредвиденной причине"
    return False, "✔ Пост в бане опубликован"
