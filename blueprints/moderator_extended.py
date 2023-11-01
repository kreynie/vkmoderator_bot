from typing import Callable

from vkbottle.user import Message, UserLabeler

from blueprints import rules
from config import moderator_db, project_path, users_db
from helpfuncs import DictionaryFuncs, functions as funcs, JSONHandler, vkfunctions as vkf
from utils.exceptions import handle_errors_decorator

moderator_extended_labeler = UserLabeler()
moderator_extended_labeler.vbml_ignore_case = True
moderator_extended_labeler.custom_rules["access"] = rules.CheckPermissions

formatted_json = JSONHandler(project_path / "formatted.json")


@moderator_extended_labeler.private_message(
    access=[rules.Groups.MODERATOR, rules.Rights.MIDDLE],
    text=[
        "Добмод <user> <key:int>",
        "Добмод <user>",
        "Добмод",
    ],
)
@handle_errors_decorator
async def add_moderator(
    message: Message,
    user: str = None,
    key: int = None,
) -> None:
    if key is None:
        return await message.answer("Забыл МВ")
    if user is None:
        return await message.answer("Забыл ссылку на страницу!")

    user_info = await vkf.get_user_info(user)

    if await moderator_db.has_user(user_info.id):
        return await message.answer("Пользователь уже есть в списке")

    if not await users_db.has_user(user_info.id):
        await users_db.add_user(user_info.id, user_info.first_name, user_info.last_name)

    is_added = await moderator_db.add_user(user_info.id, key, 1)
    if is_added:
        return await message.answer("Добавлен")

    await message.answer("Что-то пошло не так")


@moderator_extended_labeler.private_message(
    access=[rules.Groups.MODERATOR, rules.Rights.MIDDLE],
    text=[
        "Удалмод <user>",
        "Удалмод",
    ],
)
@handle_errors_decorator
async def delete_moderator(message: Message, user: str = None) -> None:
    if user is None:
        return await message.answer("Нет ссылки на страницу!")

    user_info = await vkf.get_user_info(user)

    if not await moderator_db.has_user(user_info.id):
        return await message.answer("Пользователя нет в списке")

    code = await moderator_db.remove_user(user_info.id)
    if code:
        await message.answer("Удален")
    else:
        await message.answer("Что-то пошло не так")


@moderator_extended_labeler.private_message(
    access=[rules.Groups.MODERATOR, rules.Rights.MIDDLE],
    text="Модсписок",
)
async def list_moderators(message: Message) -> None:
    leads = await moderator_db.get_all(condition={"allowance =": 3})
    moderators = leads + await moderator_db.get_all(condition={"allowance <>": 3})
    reformatted = funcs.get_moderator_list(moderators, "moderators")
    await message.answer(
        f"Модераторы с правами у бота:\n{reformatted}"
        if reformatted
        else "Ни у кого нет прав"
    )


@moderator_extended_labeler.private_message(
    access=[rules.Groups.MODERATOR, rules.Rights.MIDDLE],
    text=[
        "Добсокр <abbreviation> <full_text>",
        "Добсокр <abbreviation>",
        "Добсокр",
    ],
)
async def add_abbreviation(
    message: Message,
    abbreviation: str = None,
    full_text: str = None,
) -> None:
    if abbreviation is None or full_text is None:
        return await message.answer("Забыл сокращение или полный текст")
    reply = handle_abbreviation(
        abbreviation=abbreviation,
        action=DictionaryFuncs.add_value,
        action_success_message="добавлено",
        full_text=full_text,
    )
    await message.answer(reply)


@moderator_extended_labeler.private_message(
    access=[rules.Groups.MODERATOR, rules.Rights.MIDDLE],
    text=[
        "Измсокр <abbreviation> <full_text>",
        "Измсокр <abbreviation>",
        "Измсокр",
    ],
)
async def edit_abbreviation(
    message: Message,
    abbreviation: str = None,
    full_text: str = None,
) -> None:
    if abbreviation is None or full_text is None:
        return await message.answer("Забыл сокращение или полный текст")
    reply = handle_abbreviation(
        abbreviation=abbreviation,
        action=DictionaryFuncs.edit_value,
        action_success_message="изменено",
        full_text=full_text,
    )
    await message.answer(reply)


@moderator_extended_labeler.private_message(
    access=[rules.Groups.MODERATOR, rules.Rights.MIDDLE],
    text=["Удалсокр <abbreviation>", "Удалсокр"],
)
async def remove_abbreviation(message: Message, abbreviation: str = None) -> None:
    if abbreviation is None:
        return await message.answer("Забыл сокращение")
    reply = handle_abbreviation(
        abbreviation=abbreviation,
        action=DictionaryFuncs.remove_key,
        action_success_message="удалено",
        full_text=None,
    )
    await message.answer(reply)


def handle_abbreviation(
    abbreviation: str,
    action: Callable,
    action_success_message: str,
    full_text: str | None,
) -> str:
    formatted_dict = formatted_json.get_data()

    result, updated_abbreviations = action(
        formatted_dict,
        f"abbreviations{DictionaryFuncs.separator}{abbreviation}",
        full_text,
    )

    match result:
        case "success":
            formatted_dict["abbreviations"] = updated_abbreviations
            formatted_json.save_data(formatted_dict)
            return f"Сокращение «{abbreviation}» {action_success_message}"
        case "exists":
            return f"Сокращение «{abbreviation}» уже есть в списке"
        case "not_found":
            return f"Сокращения «{abbreviation}» нет в списке"
