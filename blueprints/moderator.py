from asyncio import sleep as asleep
from time import localtime, strftime

from config import moderator_db
from helpfuncs.functions import PhotoHandler, ReformatHandler, async_list_generator
from helpfuncs.vkfunctions import VKHandler
from vkbottle import VKAPIError
from vkbottle.user import Message, UserLabeler

from .rules import CheckPermissions, Groups, Rights

moderator_labeler = UserLabeler()
moderator_labeler.vbml_ignore_case = True
moderator_labeler.custom_rules["access"] = CheckPermissions


@moderator_labeler.private_message(
    access=[Groups.MODERATOR, Rights.LOW],
    text=[
        "Бан <user> <comment> <ban_time> <moderator_id>",
        "Бан <user> <comment> <ban_time>",
    ],
)
async def ban(message: Message, user, ban_time, comment="", moderator_id="") -> None:
    return_reason = None

    full_info = await VKHandler.get_user_info(user)
    # already_banned = await VKHandler.check_if_banned(full_info["id"])
    # if already_banned:
    #     await message.answer("Пользователь уже забанен в группе")
    #     return

    reformatter = ReformatHandler(ban_time)
    full_comment = await reformatter.reformat_comment(comment.lower())
    ban_time_text = await reformatter.reformat_time_to_text()

    if full_info is None:
        return_reason = "Ошибка получения информации из ссылки"
    if full_comment is None:
        return_reason = "Проверь ПРИЧИНУ бана"
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
                f"⚠️Ошибка получения информации\n" "Проверь картинки для бани"
            )
            return

    if moderator_id.startswith("\\"):
        moderator_id = moderator_id[1:]
        moderator_vk = await moderator_db.get_user_by_id(int(moderator_id.strip("МВ")))
    else:
        banner = await moderator_db.get_user_by_id(message.from_id)
        level = await reformatter.reformat_moderator_id(banner.get("allowance"), "МВ")
        moderator_id = level + str(banner["key"])

    time_unix = await reformatter.reformat_time()
    try:
        await VKHandler.ban(
            owner_id=full_info["id"],
            end_date=time_unix,
            reason=0,
            comment=f"{full_comment} | {moderator_id}",
            comment_visible=True,
        )
    except:
        await message.answer(f"Ошибка при попытке бана")
        raise

    if time_unix is None:
        ftime = "насвегда"
    else:
        ftime = f"\nБолеть будет до {strftime('%d.%m.%y %H:%M', localtime(time_unix))}"

    await message.answer(
        f"{full_info['first_name']} {full_info['last_name']} получил банхаммером {ftime}\n"
    )

    if photos:
        await post(
            message=message,
            photos=photos,
            moderator_vk=moderator_vk,
            moderator_id=moderator_id,
            full_info=full_info,
            comment=comment,
            ban_time=ban_time,
        )

    await asleep(3)


async def post(
    message: Message,
    photos: list,
    moderator_vk: int,
    moderator_id: str,
    full_info: dict,
    comment: str,
    ban_time: str,
) -> None:
    try:
        uploaded_photos = []
        async for photo in async_list_generator(photos):
            photo_handler = PhotoHandler(photo=photo.sizes)
            photo = await photo_handler.get_photo()
            data = await VKHandler.upload_image(photo)
            uploaded_photos.append(data)
            del photo  # deletes image from memory after uploading it to VK server

        user_full_name = f'{full_info["first_name"]} {full_info["last_name"]}'
        reply = (
            f"{user_full_name}",
            f"https://vk.com/id{full_info['id']}",
            f"{comment} - {ban_time}",
            f"@id{moderator_vk}({moderator_id})\n",
        )

        await VKHandler.post(
            from_group=True,
            message="\n".join(reply),
            attachments=uploaded_photos,
        )
        await message.answer("Пост в бане успешно сделан")
    except VKAPIError:
        await message.answer(
            "Что-то пошло не так при попытке сделать пост. Попробуй еще раз. Если не получится, то запость сам\n"
            "Напиши @volonteerblitz(ему) время попытки использования бота."
        )
