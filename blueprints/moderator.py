from asyncio import sleep as asleep
from time import localtime, strftime

from vkbottle import VKAPIError
from vkbottle.user import Message, UserLabeler

from config import moderator_db
from helpfuncs import VKHandler
from helpfuncs.functions import ReformatHandler
from utils.exceptions import handle_errors_decorator
from utils.info_classes import UserInfo
from .rules import CheckPermissions, Groups, Rights

moderator_labeler = UserLabeler()
moderator_labeler.vbml_ignore_case = True
moderator_labeler.custom_rules["access"] = CheckPermissions


@moderator_labeler.private_message(
    access=[Groups.MODERATOR, Rights.LOW],
    text=[
        "Бан <user> <comment> <ban_time> <banner_key>",
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
    ban_time: str = "",
    comment: str = "",
    banner_key: str = "",
) -> None:
    if not user:
        await message.answer(
            'Нет нарушителя. Воспользуйся командой "Помощь" для справки'
        )
        return
    if not comment:
        await message.answer("Забыл причину бана")
        return

    return_reason = None

    user_info = await VKHandler.get_user_info(user)

    already_banned = await VKHandler.check_if_banned(user_info.id)
    if already_banned:
        await message.answer("Пользователь уже забанен в группе")
        return

    reformatter = ReformatHandler(ban_time)
    full_comment = await reformatter.comment(comment.lower())
    ban_time_text = await reformatter.time_to_text()

    if user_info is None:
        return_reason = "Ошибка получения информации из ссылки"
    if full_comment is None:
        return_reason = 'Проверь ПРИЧИНУ бана (команда "сокращения")'
    if ban_time_text is None:
        return_reason = "Проверь ВРЕМЯ бана"

    if return_reason is not None:
        await message.answer(f"⚠️Ошибка получения информации\n{return_reason}")
        return

    photos = []
    if (
        ban_time_text.split()[-1] not in ("час", "сутки", "день")
        or comment.lower() == "ода"
    ):
        photos = message.get_photo_attachments()
        if not photos:
            await message.answer(
                "⚠️Ошибка получения информации\n \
                    Проверь картинки для бани"
            )
            return

    if banner_key.startswith("\\"):
        banner_key = banner_key[1:]
        banner = await moderator_db.get_user_by_id(int(banner_key.strip("МВ")))
    else:
        banner = await moderator_db.get_user_by_id(message.from_id)
        level = await reformatter.moderator_id(banner.allowance, "МВ")
        banner_key = level + str(banner.key)

    time_unix = await reformatter.time()
    try:
        await VKHandler.ban(
            owner_id=user_info.id,
            end_date=time_unix,
            reason=0,
            comment=f"{full_comment} | {banner_key}",
            comment_visible=True,
        )
    except Exception:
        await message.answer("Ошибка при попытке бана")
        raise

    if time_unix is None:
        ftime = "навсегда"
    else:
        ftime = f"\nБолеть будет до {strftime('%d.%m.%y %H:%M', localtime(time_unix))}"

    await message.answer(f"{user_info.full_name} получил банхаммером {ftime}\n")

    if photos:
        await post(
            message=message,
            photos=photos,
            banner_id=banner.id,
            banner_key=banner_key,
            user_info=user_info,
            comment=comment,
            ban_time=ban_time,
        )

    await asleep(3)


@handle_errors_decorator
async def post(
    message: Message,
    photos: list,
    banner_id: int,
    banner_key: str,
    user_info: UserInfo,
    comment: str,
    ban_time: str,
) -> None:
    uploaded_photos = await VKHandler.upload_images(photos)
    reply = (
        f"{user_info.full_name}",
        f"https://vk.com/id{user_info.id}",
        f"{comment} - {ban_time}",
        f"@id{banner_id}({banner_key})\n",
    )

    await VKHandler.post(
        from_group=True,
        message="\n".join(reply),
        attachments=uploaded_photos,
    )
    await message.answer("Пост в бане успешно сделан")
