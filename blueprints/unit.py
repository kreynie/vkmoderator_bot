from re import search

from vkbottle import VKAPIError
from vkbottle.user import Message, UserLabeler

from helpfuncs.functions import reformatModeratorDict
from helpfuncs.jsonfunctions import (
    addModerator,
    deleteModerator,
    getData,
    findModeratorByID,
)
from helpfuncs.vkfunctions import getUserInfo

from .rules import IsUnit

unit_labeler = UserLabeler()
unit_labeler.vbml_ignore_case = True


@unit_labeler.private_message(IsUnit(), text="Помощь")
async def unitCommands(message: Message):
    await message.answer(
        "\n".join(
            [
                "Список актуальных команд для юнита:",
                "▶️ Добмод <vkID> <MBid>, где <vkID> - ссылка на страницу, <MBid> - НОМЕР модератора",
                "Пример: Добмод vk.com/steel_wg 69",
                "▶️ Удалмод <vkID>, где <vkID> - ссылка на страницу",
                "▶️ Модсписок",
                "▶️ Минус <текст> - используется вместе с репостом неправильного бана из Бани в ЛС боту. Текст отправляется модератору в ЛС",
                "▶️ Сокращения",
            ]
        )
    )


@unit_labeler.private_message(IsUnit(), text="Добмод <vkID> <MBid:int>")
async def addModeratorVK(message: Message, vkID, MBid: int = 1):
    if vkID is None:
        await message.answer("Забыл ссылку на страницу!")
        return

    userInfo = await getUserInfo(vkID)
    if userInfo == None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return
    result = await addModerator(
        str(userInfo["id"]),
        {
            "ID": MBid,
            "first_name": userInfo["first_name"],
            "last_name": userInfo["last_name"],
        },
    )
    if result == "exists":
        await message.answer("Модератор уже добавлен")
    if result == "success":
        await message.answer("Модератор добавлен в список")


@unit_labeler.private_message(IsUnit(), text="Удалмод <vkID>")
async def deleteModeratorVK(message: Message, vkID):
    if vkID is None:
        await message.answer("Забыл ссылку на страницу!")
        return

    userInfo = await getUserInfo(vkID)
    if userInfo == None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return
    result = await deleteModerator(str(userInfo["id"]))
    if result == "notExists":
        await message.answer("Модератора нет в списке")
    if result == "success":
        await message.answer("Модератор был убран из списка")


@unit_labeler.private_message(IsUnit(), text="Модсписок")
async def checkModeratorsVK(message: Message):
    data = await getData()
    reformatted = await reformatModeratorDict(data["units"], "SМВ")
    reformatted += await reformatModeratorDict(data["moderators"])
    await message.answer(f"Модераторы с правами у бота:\n{reformatted}")


@unit_labeler.private_message(IsUnit(), text="Минус <reason>")
async def matchIncorrectBan(message: Message, reason: str = ""):
    if message.attachments is None:
        await message.answer("Не найден пересланный пост")
        return
    if message.attachments[0].wall is None:
        await message.answer("Переслан не пост")
        return

    postText = message.attachments[0].wall.text
    matchModeratorID = search(r".*((М|M)(В|B)\d+).*", postText)
    if matchModeratorID is None:
        await message.answer("Не удалось найти МВ в тексте поста")
        return

    try:
        moderatorVKID = await findModeratorByID(matchModeratorID.group(0))
        senderInfo = await message.get_user()
        reason = f"⚠️ {senderInfo.first_name} {senderInfo.last_name} нашел ошибку в твоем бане.\nКомментарий: {reason}"
        await message.ctx_api.messages.send(int(moderatorVKID), 0, message=reason)
    except VKAPIError:
        await message.answer("ВК не дал отправить сообщение модератору")
    except:
        await message.answer(
            "Возникла неизвестная ошибка при попытке отправить сообщение модератору\n"
            "Напиши @volonteersblitz с указанием времени попытки"
        )
        raise
