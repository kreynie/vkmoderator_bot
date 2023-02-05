from asyncio import sleep as asleep
from os import remove
from time import localtime, strftime

from vkbottle import VKAPIError
from vkbottle.user import Message, UserLabeler

import helpfuncs.functions as functions
from helpfuncs.jsonfunctions import getData
from helpfuncs.vkfunctions import banUser, getUserInfo, post, uploadImage

from .rules import CheckRights, Rights

moderator_labeler = UserLabeler()
moderator_labeler.vbml_ignore_case = True
moderator_labeler.custom_rules["access"] = CheckRights


@moderator_labeler.private_message(
    access=Rights.moderator,
    text=[
        "Бан <userID> <comment> <time> <moderatorID>",
        "Бан <userID> <comment> <time>",
    ],
)
async def banAndPost(message: Message, userID, time=None, comment="", moderatorID=""):
    returnReason = None

    fullInfo = await getUserInfo(userID)
    fullComment = await functions.reformatComment(comment.lower())
    banTimeText = await functions.timeToText(time)

    if fullInfo is None:
        returnReason = "Ошибка получения информации из ссылки"
    if fullComment is None:
        returnReason = "Проверь ПРИЧИНУ бана"
    if banTimeText == 0:
        returnReason = "Проверь ВРЕМЯ бана"

    if returnReason is not None:
        await message.answer(f"⚠️Ошибка получения информации\n{returnReason}")
        return

    photos = []
    if banTimeText[3:] not in ("час", "сутки", "день") or comment.lower() == "ода":
        photos = message.get_photo_attachments()
        if photos == []:
            await message.answer(
                f"⚠️Ошибка получения информации\n" "Проверь картинки для бани"
            )
            return

    full_name = f'{fullInfo["first_name"]} {fullInfo["last_name"]}'

    if not moderatorID.startswith("\\"):
        moderatorID = await getData()
        banner = moderatorID[str(message.from_id)]
        level = await functions.reformatModeratorID(banner["rights"])
        moderatorID = level + str(banner["ID"])
    else:
        moderatorID = moderatorID[1:]

    time = await functions.reformatTime(time)
    await banUser(
        fullInfo["id"],
        time,
        0,
        f"{fullComment} | {moderatorID}",
        True,
    )

    if time is not None:
        tempTime = localtime(await functions.reformatTime(time))
        fTime = strftime("%d.%m.%y %H:%M", tempTime)
        await message.answer(
            f"{full_name} получил банхаммером\n" f"Болеть будет до {fTime}"
        )
        del tempTime, fTime

    if photos != []:
        try:
            pics = []
            async for photo in functions.asyncListGenerator(photos):
                url = await functions.getMaxSizePhotoURL(photo.sizes)
                filename = await functions.downloadPhoto(url)
                data = await uploadImage(filename)
                remove(filename)
                pics.append(data)

            reply = (
                f"{full_name}",
                f"https://vk.com/id{fullInfo['id']}",
                f"{comment} - {banTimeText[3:]}",
                f"@id{message.from_id}({moderatorID})\n",
                "made with Moderator Bot",
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
