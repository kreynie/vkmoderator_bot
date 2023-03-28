from config import moderator_db, users_db
from helpfuncs import DictionaryFuncs, JSONHandler, VKHandler
from helpfuncs.functions import ReformatHandler
from vkbottle.user import Message, UserLabeler

from .rules import CheckPermissions, Groups, Rights

moderext_labeler = UserLabeler()
moderext_labeler.vbml_ignore_case = True
moderext_labeler.custom_rules["access"] = CheckPermissions

formatted_json = JSONHandler("formatted.json")


@moderext_labeler.private_message(
    access=[Groups.MODERATOR, Rights.MIDDLE],
    text="Добмод <user> <key:int>",
)
async def add_moderator(
    message: Message,
    user: str = None,
    key: int = None,
) -> None:
    if user is None:
        await message.answer("Забыл ссылку на страницу!")
        return
    if key is None:
        await message.answer("Забыл МВ")
        return

    user_info = await VKHandler.get_user_info(user)
    if user_info is None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return

    if await moderator_db.has_user(user_info.id):
        await message.answer("Пользователь уже есть в списке")
        return

    if not await users_db.has_user(user_info.id):
        await users_db.add_user(user_info.id, user_info.first_name, user_info.last_name)

    code = await moderator_db.add_user(user_info.id, key, 1)
    if code:
        await message.answer("Добавлен")
    else:
        await message.answer("Что-то пошло не так")


@moderext_labeler.private_message(
    access=[Groups.MODERATOR, Rights.MIDDLE],
    text="Удалмод <user>",
)
async def delete_moderator(message: Message, user: str = None) -> None:
    if user is None:
        await message.answer("Забыл ссылку на страницу!")
        return

    user_info = await VKHandler.get_user_info(user)
    if user_info is None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return

    if not await moderator_db.has_user(user_info.id):
        await message.answer("Пользователя нет в списке")
        return

    code = await moderator_db.remove_user(user_info.id)
    if code:
        await message.answer("Удален")
    else:
        await message.answer("Что-то пошло не так")


@moderext_labeler.private_message(
    access=[Groups.MODERATOR, Rights.MIDDLE],
    text="Модсписок",
)
async def list_moderators(message: Message) -> None:
    moderators = await moderator_db.get_all()
    reformatted = await ReformatHandler.moderator_list(moderators, "moderators")
    await message.answer(
        f"Модераторы с правами у бота:\n{reformatted}"
        if reformatted
        else "Ни у кого нет прав"
    )


@moderext_labeler.private_message(
    access=[Groups.MODERATOR, Rights.MIDDLE],
    text="Добсокр <abbreviation> <full_text>",
)
async def add_abbreviation(
    message: Message,
    abbreviation: str = None,
    full_text: str = None,
) -> None:
    if abbreviation is None or full_text is None:
        await message.answer("Забыл сокращение или полный текст")
        return
    formatted_dict = formatted_json.get_data()
    result, updated_abbreviations = await DictionaryFuncs.add_value(
        formatted_dict["abbreviations"],
        abbreviation,
        full_text.lower(),
    )
    match result:
        case "success":
            formatted_dict["abbreviations"] = updated_abbreviations
            formatted_json.save_data(formatted_dict)
            await message.answer(f"Сокращение «{abbreviation}» добавлено")
        case "exists":
            await message.answer(f"Сокращение «{abbreviation}» уже есть в списке")


@moderext_labeler.private_message(
    access=[Groups.MODERATOR, Rights.MIDDLE],
    text="Измсокр <abbreviation> <full_text>",
)
async def edit_abbreviation(
    message: Message,
    abbreviation: str = None,
    full_text: str = None,
) -> None:
    if abbreviation is None or full_text is None:
        await message.answer("Забыл сокращение или полный текст")
        return
    formatted_dict = formatted_json.get_data()
    result, updated_abbreviations = await DictionaryFuncs.edit_value(
        formatted_dict,
        f"abbreviations{DictionaryFuncs.separator}{abbreviation}",
        full_text.lower(),
    )
    match result:
        case "success":
            formatted_dict["abbreviations"] = updated_abbreviations
            formatted_json.save_data(formatted_dict)
            await message.answer(f"Сокращение «{abbreviation}» изменено")
        case "not_found":
            await message.answer(f"Сокращения «{abbreviation}» нет в списке")
        case _:
            await message.answer(f"Что-то пошло не так. Код ошибки: {result}")


@moderext_labeler.private_message(
    access=[Groups.MODERATOR, Rights.MIDDLE],
    text="Удалсокр <abbreviation>",
)
async def remove_abbreviation(message: Message, abbreviation: str = None) -> None:
    if abbreviation is None:
        await message.answer("Забыл сокращение")
        return
    formatted_dict = formatted_json.get_data()
    result, updated_abbreviations = await DictionaryFuncs.remove_key(
        formatted_dict, f"abbreviations{DictionaryFuncs.separator}{abbreviation}"
    )
    match result:
        case "success":
            formatted_dict["abbreviations"] = updated_abbreviations
            formatted_json.save_data(formatted_dict)
            await message.answer(f"Сокращение «{abbreviation}» удалено")
        case "not_found":
            await message.answer(f"Сокращения «{abbreviation}» нет в списке")
        case _:
            await message.answer(f"Что-то пошло не так. Код ошибки: {result}")
