from vkbottle.user import Message, UserLabeler

from helpfuncs.functions import ReformatHandler
from helpfuncs.jsonfunctions import DictionaryFuncs, JSONHandler, ModeratorHandler
from helpfuncs.vkfunctions import VKHandler

from .rules import CheckPermissions, Groups, Rights

moderext_labeler = UserLabeler()
moderext_labeler.vbml_ignore_case = True
moderext_labeler.custom_rules["access"] = CheckPermissions

moderator_json = JSONHandler("moderators.json")
formatted_json = JSONHandler("formatted.json")


@moderext_labeler.private_message(
    access=[Groups.MODERATOR, Rights.MIDDLE],
    text="Добмод <vk_id> <MB_id:int>",
)
async def add_moderator(
    message: Message,
    vk_id: str,
    MB_id: int,
) -> None:
    moderator_handler = await ModeratorHandler.create()
    if not vk_id:
        await message.answer("Забыл ссылку на страницу!")
        return

    user_info = await VKHandler.get_user_info(vk_id)
    if user_info is None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return

    moderator_data = {
        "ID": MB_id,
        "first_name": user_info["first_name"],
        "last_name": user_info["last_name"],
    }
    result = await moderator_handler.add_moderator(
        str(user_info["id"]), moderator_data, Groups.MODERATOR
    )

    if result == "exists":
        await message.answer("Модератор уже добавлен")
    elif result == "success":
        await message.answer("Модератор добавлен в список")


@moderext_labeler.private_message(
    access=[Groups.MODERATOR, Rights.MIDDLE], text="Удалмод <vk_id>"
)
async def delete_moderator(message: Message, vk_id) -> None:
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


@moderext_labeler.private_message(
    access=[Groups.MODERATOR, Rights.MIDDLE], text="Модсписок"
)
async def check_moderators(message: Message) -> None:
    data = moderator_json.get_data()
    reformatted = await ReformatHandler.reformat_moderator_dict(data, "moderator")
    await message.answer(f"Модераторы с правами у бота:\n{reformatted}")


@moderext_labeler.private_message(
    access=[Groups.MODERATOR, Rights.MIDDLE], text="Добсокр <abbreviation> <full_text>"
)
async def add_abbreviation(message: Message, abbreviation: str, full_text: str) -> None:
    if abbreviation is None or full_text is None:
        await message.answer("Забыл сокращения или полный текст")
        return
    formatted_dict = formatted_json.get_data()
    result, updated_abbreviations = await DictionaryFuncs.add_value(
        formatted_dict["abbreviations"],
        abbreviation,
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


@moderext_labeler.private_message(
    access=[Groups.MODERATOR, Rights.MIDDLE], text="Измсокр <abbreviation> <full_text>"
)
async def edit_abbreviation(
    message: Message, abbreviation: str, full_text: str
) -> None:
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
