from vkbottle.user import Message, UserLabeler

from helpfuncs.functions import Reformatter
from helpfuncs.jsonfunctions import JSONHandler, ModeratorHandler
from helpfuncs.vkfunctions import get_user_info

from .rules import CheckRights, Rights


moderext_labeler = UserLabeler()
moderext_labeler.vbml_ignore_case = True
moderext_labeler.custom_rules["access"] = CheckRights
json_handler = JSONHandler()


@moderext_labeler.private_message(
    access=Rights.supermoderator,
    text="Добмод <vk_id> <MBid:int>",
)
async def addModeratorVK(message: Message, vk_id, MBid: int = 1):
    moderator_handler = await ModeratorHandler.create()
    if vk_id is None:
        await message.answer("Забыл ссылку на страницу!")
        return

    user_info = await get_user_info(vk_id)
    if user_info == None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return
    result = await moderator_handler.add_moderator(
        str(user_info["id"]),
        {
            "ID": MBid,
            "first_name": user_info["first_name"],
            "last_name": user_info["last_name"],
            "rights": 1,
            "groups": [],
        },
    )
    if result == "exists":
        await message.answer("Модератор уже добавлен")
    if result == "success":
        await message.answer("Модератор добавлен в список")


@moderext_labeler.private_message(access=Rights.supermoderator, text="Удалмод <vk_id>")
async def deleteModeratorVK(message: Message, vk_id):
    moderator_handler = await ModeratorHandler.create()
    if vk_id is None:
        await message.answer("Забыл ссылку на страницу!")
        return

    user_info = await get_user_info(vk_id)
    if user_info == None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return
    result = await moderator_handler.delete_moderator(str(user_info["id"]))
    if result == "not_exists":
        await message.answer("Модератора нет в списке")
    if result == "success":
        await message.answer("Модератор был убран из списка")


@moderext_labeler.private_message(access=Rights.supermoderator, text="Модсписок")
async def checkModeratorsVK(message: Message):
    data = json_handler.get_data()
    reformatted = await Reformatter.reformat_moderator_dict(data)
    await message.answer(f"Модераторы с правами у бота:\n{reformatted}")
