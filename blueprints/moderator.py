from asyncio import sleep as asleep
from time import localtime, strftime

from vkbottle import VKAPIError
from vkbottle.user import Message, UserLabeler

from helpfuncs.functions import PhotoHandler, ReformatHandler, async_list_generator
from helpfuncs.jsonfunctions import JSONHandler, ModeratorHandler
from helpfuncs.vkfunctions import VKHandler

from .rules import CheckPermissions, Groups, Rights

moderator_labeler = UserLabeler()
moderator_labeler.vbml_ignore_case = True
moderator_labeler.custom_rules["access"] = CheckPermissions
json_handler = JSONHandler()


@moderator_labeler.private_message(
    access=[Groups.MODERATOR, Rights.LOW],
    text=[
        "Бан <user_id> <comment> <ban_time> <moderator_id>",
        "Бан <user_id> <comment> <ban_time>",
    ],
)
async def ban_and_post(
    message: Message, user_id, ban_time, comment="", moderator_id=""
) -> None:
    return_reason = None

    full_info = await VKHandler.get_user_info(user_id)
    already_banned = await VKHandler.check_if_banned(full_info["id"])
    if already_banned:
        await message.answer("Пользователь уже забанен в группе")
        return

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
        if photos == []:
            await message.answer(
                f"⚠️Ошибка получения информации\n" "Проверь картинки для бани"
            )
            return

    moderator_handler = await ModeratorHandler.create()

    user_full_name = f'{full_info["first_name"]} {full_info["last_name"]}'

    if moderator_id.startswith("\\"):
        moderator_id = moderator_id[1:]
        moderator_vk = await moderator_handler.find_moderator_by_id(moderator_id)
    else:
        moderator_id = json_handler.get_data()
        moderator_vk = str(message.from_id)
        banner = moderator_id[moderator_vk]
        level = await reformatter.reformat_moderator_id(
            banner.get("groups").get("moderator")
        )
        moderator_id = level + str(banner["ID"])

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
        return

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
                file = await photo_handler.get_photo()
                data = await VKHandler.upload_image(file)
                pics.append(data)
                del file  # deletes image from memory after uploading it to VK server

            reply = (
                f"{user_full_name}",
                f"https://vk.com/id{full_info['id']}",
                f"{comment} - {ban_time}",
                f"@id{moderator_vk}({moderator_id})\n",
            )

            await VKHandler.post(
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
