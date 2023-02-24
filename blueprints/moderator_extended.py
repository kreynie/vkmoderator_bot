from vkbottle.user import Message, UserLabeler

from helpfuncs.functions import ReformatHandler
from helpfuncs.jsonfunctions import JSONHandler, ModeratorHandler, DictionaryFuncs
from helpfuncs.vkfunctions import VKHandler

from .rules import CheckRights, Rights


moderext_labeler = UserLabeler()
moderext_labeler.vbml_ignore_case = True
moderext_labeler.custom_rules["access"] = CheckRights
moderator_json = JSONHandler("moderators.json")
formatted_json = JSONHandler("formatted.json")


@moderext_labeler.private_message(
    access=Rights.supermoderator,
    text="Добмод <vk_id> <MBid:int>",
)
async def addModeratorVK(message: Message, vk_id, MBid: int = 1):
    moderator_handler = await ModeratorHandler.create()
    if vk_id is None:
        await message.answer("Забыл ссылку на страницу!")
        return

    user_info = await VKHandler.get_user_info(vk_id)
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

    user_info = await VKHandler.get_user_info(vk_id)
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
    data = moderator_json.get_data()
    reformatted = await ReformatHandler.reformat_moderator_dict(data)
    await message.answer(f"Модераторы с правами у бота:\n{reformatted}")


@moderext_labeler.private_message(
    access=Rights.supermoderator, text="Добсокр <abbreviation> <full_text>"
)
async def add_abbreviation(message: Message, abbreviation: str, full_text: str):
    if abbreviation is None or full_text is None:
        await message.answer("Забыл сокращения или полный текст")
        return
    formatted_dict = formatted_json.get_data()
    result, updated_abbreviations = await DictionaryFuncs.add_value(
        formatted_dict,
        f"abbreviations{DictionaryFuncs.separator}{abbreviation}",
        full_text.lower(),
    )
    match result:
        case "success":
            await message.answer(f"Сокращение «{abbreviation}» добавлено")
            formatted_dict["abbreviations"] = updated_abbreviations
            formatted_json.save_data(formatted_dict)
            return
        case "exists":
            await message.answer(f"Сокращение «{abbreviation}» уже есть в списке")
            return
        case _:
            await message.answer(f"Что-то пошло не так. Код ошибки: {result}")


@moderext_labeler.private_message(
    access=Rights.supermoderator, text="Измсокр <abbreviation> <full_text>"
)
async def add_abbreviation(message: Message, abbreviation: str, full_text: str):
    if abbreviation is None or full_text is None:
        await message.answer("Забыл сокращения или полный текст")
        return
    formatted_dict = formatted_json.get_data()
    result, updated_abbreviations = await DictionaryFuncs.edit_value(
        formatted_dict,
        f"abbreviations{DictionaryFuncs.separator}{abbreviation}",
        full_text.lower(),
    )
    match result:
        case "success":
            await message.answer(f"Сокращение «{abbreviation}» изменено")
            formatted_dict["abbreviations"] = updated_abbreviations
            formatted_json.save_data(formatted_dict)
            return
        case "not_found":
            await message.answer(f"Сокращения «{abbreviation}» нет в списке")
            return
        case _:
            await message.answer(f"Что-то пошло не так. Код ошибки: {result}")
