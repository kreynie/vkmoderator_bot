from asyncio import sleep as asleep
from os import remove
from time import localtime, strftime

from vkbottle import VKAPIError
from vkbottle.user import Message, UserLabeler

import helpfuncs.functions as functions
from helpfuncs.jsonfunctions import get_data
from helpfuncs.vkfunctions import ban, get_user_info, post, upload_image

from .rules import CheckRights, Rights

moderator_labeler = UserLabeler()
moderator_labeler.vbml_ignore_case = True
moderator_labeler.custom_rules["access"] = CheckRights


@moderator_labeler.private_message(
    access=Rights.moderator,
    text=[
        "Бан <user_id> <comment> <ban_time> <moderator_id>",
        "Бан <user_id> <comment> <ban_time>",
    ],
)
async def ban_and_post(
    message: Message, user_id, ban_time, comment="", moderator_id=""
):
    return_reason = None

    full_info = await get_user_info(user_id)
    full_comment = await functions.reformat_comment(comment.lower())
    ban_time_text = await functions.time_to_text(ban_time)

    if full_info is None:
        return_reason = "Ошибка получения информации из ссылки"
    if full_comment is None:
        return_reason = "Проверь ПРИЧИНУ бана"
    if ban_time_text == 0:
        return_reason = "Проверь ВРЕМЯ бана"

    if return_reason is not None:
        await message.answer(f"⚠️Ошибка получения информации\n{return_reason}")
        return

    photos = []
    if ban_time_text[3:] not in ("час", "сутки", "день") or comment.lower() == "ода":
        photos = message.get_photo_attachments()
        if photos == []:
            await message.answer(
                f"⚠️Ошибка получения информации\n" "Проверь картинки для бани"
            )
            return

    user_full_name = f'{full_info["first_name"]} {full_info["last_name"]}'

    if not moderator_id.startswith("\\"):
        moderator_id = await get_data()
        banner = moderator_id[str(message.from_id)]
        level = await functions.reformat_moderator_id(banner["rights"])
        moderator_id = level + str(banner["ID"])
    else:
        moderator_id = moderator_id[1:]

    time_unix = await functions.reformat_time(ban_time)
    await ban(
        full_info["id"],
        time_unix,
        0,
        f"{full_comment} | {moderator_id}",
        True,
    )

    if time_unix is None:
        ftime = "насвегда"
    else:
        temp_time = strftime("%d.%m.%y %H:%M", localtime(time_unix))
        ftime = f"\nБолеть будет до {temp_time}"

    await message.answer(f"{user_full_name} получил банхаммером {ftime}\n")
    del temp_time, ftime

    if photos != []:
        try:
            pics = []
            async for photo in functions.async_list_generator(photos):
                url = await functions.get_max_size_photo_URL(photo.sizes)
                filename = await functions.download_photo(url)
                data = await upload_image(filename)
                remove(filename)
                pics.append(data)

            reply = (
                f"{user_full_name}",
                f"https://vk.com/id{full_info['id']}",
                f"{comment} - {ban_time}",
                f"@id{message.from_id}({moderator_id})\n",
            )

            await post(
                from_group=True,
                message="\n".join(reply),
                attachments=pics,
            )
            await message.answer("Пост в бане успешно сделан")
        except VKAPIError:
            await message.answer(
                "Что-то пошло не так при попытке сделать пост. Попробуй еще раз. Если не получится, то запость сам\n"
                "Напиши @volonteerblitz(ему) время попытки использования бота."
            )

    await asleep(3)
