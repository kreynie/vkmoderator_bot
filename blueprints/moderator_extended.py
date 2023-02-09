from vkbottle.user import Message, UserLabeler

from helpfuncs.functions import Reformatter
from helpfuncs.jsonfunctions import JSONHandler, ModeratorHandler
from helpfuncs.vkfunctions import get_user_info

from .rules import CheckRights, Rights


moderext_labeler = UserLabeler()
moderext_labeler.vbml_ignore_case = True
moderext_labeler.custom_rules["access"] = CheckRights
json_handler = JSONHandler()
moderator_handler = ModeratorHandler()


@moderext_labeler.private_message(
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
    result = await moderator_handler.add_moderator(
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


@moderext_labeler.private_message(access=Rights.supermoderator, text="Удалмод <vkID>")
async def deleteModeratorVK(message: Message, vkID):
    if vkID is None:
        await message.answer("Забыл ссылку на страницу!")
        return

    userInfo = await get_user_info(vkID)
    if userInfo == None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return
    result = await moderator_handler.delete_moderator(str(userInfo["id"]))
    if result == "not_exists":
        await message.answer("Модератора нет в списке")
    if result == "success":
        await message.answer("Модератор был убран из списка")


@moderext_labeler.private_message(access=Rights.supermoderator, text="Модсписок")
async def checkModeratorsVK(message: Message):
    data = await json_handler.get_data()
    reformatted = await Reformatter().reformat_moderator_dict(data)
    await message.answer(f"Модераторы с правами у бота:\n{reformatted}")
