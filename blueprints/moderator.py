from asyncio import sleep as asleep
from os import remove
from time import localtime, strftime

from vkbottle import VKAPIError
from vkbottle.user import Message, UserLabeler

from helpfuncs.functions import Reformatter, PhotoHandler, async_list_generator
from helpfuncs.jsonfunctions import JSONHandler, ModeratorHandler
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
    reformatter = Reformatter(ban_time)
    full_comment = await reformatter.reformat_comment(comment.lower())
    ban_time_text = await reformatter.reformat_time_to_text()

    if full_info is None:
        return_reason = "Ошибка получения информации из ссылки"
    if full_comment is None:
        return_reason = "Проверь ПРИЧИНУ бана"
    if ban_time_text == None:
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
        if photos == []:
            await message.answer(
                f"⚠️Ошибка получения информации\n" "Проверь картинки для бани"
            )
            return

    json_handler = JSONHandler()
    moderator_handler = await ModeratorHandler.create()

    user_full_name = f'{full_info["first_name"]} {full_info["last_name"]}'

    if moderator_id.startswith("\\"):
        moderator_id = moderator_id[1:]
        moderator_vk = await moderator_handler.find_moderator_by_id(moderator_id)
    else:
        moderator_id = await json_handler.get_data()
        moderator_vk = str(message.from_id)
        banner = moderator_id[moderator_vk]
        level = await reformatter.reformat_moderator_id(banner["rights"])
        moderator_id = level + str(banner["ID"])

    time_unix = await reformatter.reformat_time()
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
        ftime = f"\nБолеть будет до {strftime('%d.%m.%y %H:%M', localtime(time_unix))}"

    await message.answer(f"{user_full_name} получил банхаммером {ftime}\n")
    del ftime

    if photos != []:
        try:
            pics = []
            async for photo in async_list_generator(photos):
                photo_handler = PhotoHandler(photo=photo.sizes)
                filename = await photo_handler.download_photo()
                data = await upload_image(filename)
                remove(filename)
                pics.append(data)

            reply = (
                f"{user_full_name}",
                f"https://vk.com/id{full_info['id']}",
                f"{comment} - {ban_time}",
                f"@id{moderator_vk}({moderator_id})\n",
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
