from asyncio import sleep as asleep
from time import localtime, strftime
from typing import TypeAlias

from vkbottle.user import Message, UserLabeler
from vkbottle_types.objects import PhotosPhoto

from blueprints import rules
from config import moderator_db
from helpfuncs import functions as funcs, vkfunctions as vkf
from utils import info_classes
from utils.exceptions import handle_errors_decorator

moderator_labeler = UserLabeler()
moderator_labeler.vbml_ignore_case = True
moderator_labeler.custom_rules["access"] = rules.CheckPermissions


ReturnResult: TypeAlias = tuple[str | None, str | None]


@moderator_labeler.private_message(
    access=[rules.Groups.MODERATOR, rules.Rights.LOW],
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

    user_info = await vkf.get_user_info(user)
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
        return await message.answer(f"⚠️Ошибка получения информации\n{return_reason}")

    await message.answer(ban_result)
    await asleep(3)


async def perform_ban(
    banner_vk_id: int,
    user_info: info_classes.UserInfo,
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

    banner = await get_banner_info(banner_vk_id)

    time_unix = funcs.calculate_unix_time_after_period(ban_time)

    ftime = "навсегда"
    if time_unix is not None:
        ftime = f"Болеть будет до {strftime('%d.%m.%y %H:%M', localtime(time_unix))}"

    result = await vkf.ban(
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
        ban_info = info_classes.BanRegistrationInfo(
            banner_info=banner,
            user_info=user_info,
            comment=comment,
            ban_time=ban_time_text,
        )
        post_info = await post(ban_info, attachments)
        post_info = f"\n\n{post_info}"

    return f"{user_info.full_name} получил банхаммером\n{ftime}{post_info}", None


async def get_banner_info(user_vk_id: int) -> info_classes.BannerInfo:
    banner = await moderator_db.get_user_by_id(user_vk_id)
    prefix = funcs.get_moderator_prefix(banner.allowance, "МВ")
    banner_key = prefix + str(banner.key)
    return info_classes.BannerInfo(moderator=banner, key=banner_key)


@handle_errors_decorator
async def post(
    message: Message,  # required for decorator
    ban_info: info_classes.BanRegistrationInfo,
    photos: list,
) -> str:
    uploaded_photos = await vkf.upload_images(photos)
    reply = (
        f"{ban_info.user_info.full_name}",
        f"https://vk.com/id{ban_info.user_info.id}",
        f"{ban_info.comment} - {ban_info.ban_time}",
        f"@id{ban_info.banner_info.moderator.id}({ban_info.banner_info.key})",
    )

    post_result = await vkf.post(
        from_group=True,
        message="\n".join(reply),
        attachments=uploaded_photos,
    )
    if post_result is None:
        return "❌ Не удалось сделать пост в бане"
    return "✔ Пост в бане опубликован"
