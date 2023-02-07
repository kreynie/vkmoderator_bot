from vkbottle.user import Message, UserLabeler

from helpfuncs.functions import reformat_moderator_dict
from helpfuncs.jsonfunctions import (
    add_moderator,
    delete_moderator,
    get_data,
)
from helpfuncs.vkfunctions import get_user_info

from .rules import CheckRights, Rights


supmoder_labeler = UserLabeler()
supmoder_labeler.vbml_ignore_case = True
supmoder_labeler.custom_rules["access"] = CheckRights


@supmoder_labeler.private_message(
    access=Rights.supermoderator,
    text="Добмод <vkID> <MBid:int>",
)
async def addModeratorVK(message: Message, vkID, MBid: int = 1):
    if vkID is None:
        await message.answer("Забыл ссылку на страницу!")
        return

    userInfo = await get_user_info(vkID)
    if userInfo == None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return
    result = await add_moderator(
        str(userInfo["id"]),
        {
            "ID": MBid,
            "first_name": userInfo["first_name"],
            "last_name": userInfo["last_name"],
            "rights": 1,
        },
    )
    if result == "exists":
        await message.answer("Модератор уже добавлен")
    if result == "success":
        await message.answer("Модератор добавлен в список")


@supmoder_labeler.private_message(access=Rights.supermoderator, text="Удалмод <vkID>")
async def deleteModeratorVK(message: Message, vkID):
    if vkID is None:
        await message.answer("Забыл ссылку на страницу!")
        return

    userInfo = await get_user_info(vkID)
    if userInfo == None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return
    result = await delete_moderator(str(userInfo["id"]))
    if result == "notExists":
        await message.answer("Модератора нет в списке")
    if result == "success":
        await message.answer("Модератор был убран из списка")


@supmoder_labeler.private_message(access=Rights.supermoderator, text="Модсписок")
async def checkModeratorsVK(message: Message):
    data = await get_data()
    reformatted = await reformat_moderator_dict(data)
    await message.answer(f"Модераторы с правами у бота:\n{reformatted}")
