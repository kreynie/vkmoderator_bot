from asyncio import sleep as asleep
from time import localtime, strftime
from typing import TypeAlias

from vkbottle.user import Message, UserLabeler

from config import moderator_db
from helpfuncs import VKHandler
from helpfuncs.functions import ReformatHandler
from utils.exceptions import handle_errors_decorator
from utils.info_classes import BannerInfo, BanRegistrationInfo, UserInfo
from .rules import CheckPermissions, Groups, Rights

moderator_labeler = UserLabeler()
moderator_labeler.vbml_ignore_case = True
moderator_labeler.custom_rules["access"] = CheckPermissions


ReturnResult: TypeAlias = tuple[str | None, str | None]


@moderator_labeler.private_message(
    access=[Groups.MODERATOR, Rights.LOW],
    text=[
        "Бан <user> <comment> <ban_time>",
        "Бан <user> <comment>",
        "Бан <user>",
        "Бан",
    ],
)
@handle_errors_decorator
async def ban(
    message: Message,
    user: str = "",
    comment: str = "",
    ban_time: str = "",
) -> None:
    if not user:
        return await message.answer(
            'Нет нарушителя. Воспользуйся командой "Помощь" для справки'
        )

    if not comment:
        return await message.answer("Забыл причину бана")

    user_info = await VKHandler.get_user_info(user)
    already_banned = await VKHandler.check_if_banned(user_info.id)
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
        return await message.answer(f"⚠️Ошибка получения информации\n{return_reason}")

    await message.answer(ban_result)
    await asleep(3)


async def perform_ban(
    banner_vk_id: int,
    user_info: UserInfo,
    ban_time: str,
    comment: str,
    attachments: list | None = None,
) -> ReturnResult:
    reformatter = ReformatHandler(ban_time)
    full_comment = reformatter.comment(comment)
    ban_time_text = reformatter.time_to_text()

    if full_comment is None:
        return None, 'Проверь ПРИЧИНУ бана (команда "сокращения")'

    if ban_time_text is None:
        return None, "Проверь ВРЕМЯ бана"

    is_post_needed = ban_time_text not in ("час", "сутки", "день") or comment == "ода"
    if is_post_needed and attachments is None:
        return None, "Проверь картинки для бани"

    banner = await get_banner_info(banner_vk_id)

    time_unix = reformatter.time()

    ftime = "навсегда"
    if time_unix is not None:
        ftime = f"Болеть будет до {strftime('%d.%m.%y %H:%M', localtime(time_unix))}"

    result = await VKHandler.ban(
        owner_id=user_info.id,
        end_date=time_unix,
        reason=0,
        comment=f"{full_comment} | {banner.key}",
        comment_visible=True,
    )

    if result != 1:
        return None, "Не удалось забанить человека на стороне VK"

    post_info = ""
    if is_post_needed:
        ban_info = BanRegistrationInfo(
            banner_info=banner,
            user_info=user_info,
            comment=comment,
            ban_time=ban_time,
        )
        post_info = await post(ban_info, attachments)
        post_info = f"\n\n{post_info}"

    return f"{user_info.full_name} получил банхаммером\n{ftime}{post_info}", None


async def get_banner_info(user_vk_id: int) -> BannerInfo:
    banner = await moderator_db.get_user_by_id(user_vk_id)
    level = ReformatHandler.moderator_id(banner.allowance, "МВ")
    banner_key = level + str(banner.key)
    return BannerInfo(moderator=banner, key=banner_key)


@handle_errors_decorator
async def post(
    ban_info: BanRegistrationInfo,
    photos: list,
) -> str:
    uploaded_photos = await VKHandler.upload_images(photos)
    reply = (
        f"{ban_info.user_info.full_name}",
        f"https://vk.com/id{ban_info.user_info.id}",
        f"{ban_info.comment} - {ban_info.ban_time}",
        f"@id{ban_info.banner_info.moderator.id}({ban_info.banner_info.key})",
    )

    post_result = await VKHandler.post(
        from_group=True,
        message="\n".join(reply),
        attachments=uploaded_photos,
    )
    if post_result is None:
        return "❌ Не удалось сделать пост в бане"
    return "✔ Пост в бане опубликован"
