from config import moderator_db, users_db
from helpfuncs.functions import ReformatHandler
from helpfuncs.jsonfunctions import DictionaryFuncs, JSONHandler
from helpfuncs.vkfunctions import VKHandler
from vkbottle.user import Message, UserLabeler

from .rules import CheckPermissions, Groups, Rights

moderext_labeler = UserLabeler()
moderext_labeler.vbml_ignore_case = True
moderext_labeler.custom_rules["access"] = CheckPermissions

formatted_json = JSONHandler("formatted.json")


@moderext_labeler.private_message(
    access=[Groups.MODERATOR, Rights.MIDDLE],
    text="Добмод <user> <id:int>",
)
async def add_moderator(
    message: Message,
    user: str,
    id: int,
) -> None:
    if not user:
        await message.answer("Забыл ссылку на страницу!")
        return
    if not id:
        await message.answer("Забыл МВ")
        return

    user_info = await VKHandler.get_user_info(user)
    if user_info is None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return
    user_id = user_info["id"]

    if await moderator_db.has_user(user_id):
        await message.answer("Пользователь уже есть в списке")
        return

    if not await users_db.has_user(user_id):
        await users_db.add_user(
            user_id, user_info["first_name"], user_info["last_name"]
        )

    code = await moderator_db.add_user(user_id, id, 1)
    if code:
        await message.answer("Добавлен")
    else:
        await message.answer("Что-то пошло не так")


@moderext_labeler.private_message(
    access=[Groups.MODERATOR, Rights.MIDDLE],
    text="Удалмод <user>",
)
async def delete_moderator(message: Message, user: str) -> None:
    if user is None:
        await message.answer("Забыл ссылку на страницу!")
        return

    user_info = await VKHandler.get_user_info(user)
    if user_info == None:
        await message.answer("Ссылка на страницу должна быть полной и корректной")
        return
    user_id = user_info["id"]

    if not await moderator_db.has_user(user_id):
        await message.answer("Пользователя нет в списке")
        return

    code = await moderator_db.remove_user(user_id)
    if code:
        await message.answer("Удален")
    else:
        await message.answer("Что-то пошло не так")


@moderext_labeler.private_message(
    access=[Groups.MODERATOR, Rights.MIDDLE],
    text="Модсписок",
)
async def list_moderators(message: Message) -> None:
    users = await users_db.get_all("moderators")
    reformatted = await ReformatHandler.reformat_moderator_dict(users, "moderators")
    await message.answer(
        f"Модераторы с правами у бота:\n{reformatted}"
        if reformatted
        else "Ни у кого нет прав"
    )


@moderext_labeler.private_message(
    access=[Groups.MODERATOR, Rights.MIDDLE],
    text="Добсокр <abbreviation> <full_text>",
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
        case "exists":
            await message.answer(f"Сокращение «{abbreviation}» уже есть в списке")


@moderext_labeler.private_message(
    access=[Groups.MODERATOR, Rights.MIDDLE],
    text="Измсокр <abbreviation> <full_text>",
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
        case "not_found":
            await message.answer(f"Сокращения «{abbreviation}» нет в списке")
        case _:
            await message.answer(f"Что-то пошло не так. Код ошибки: {result}")
