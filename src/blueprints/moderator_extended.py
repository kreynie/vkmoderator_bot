from typing import Callable

from vkbottle.user import Message

from config import project_path
from src.blueprints import rules
from src.helpfuncs import DictionaryFuncs, functions as funcs, JSONHandler, vkfunctions as vkf
from src.helpfuncs.list_stuffs_utils import list_stuff_groups
from src.schemas import stuff as stuff_schema, user as user_schema
from src.services import StuffsService
from src.utils.dependencies import UOWDep
from src.utils.unitofwork import IUnitOfWork
from .base_labeler import labeler

formatted_json = JSONHandler(project_path / "formatted.json")


@labeler.private_message(
    access=[rules.StuffGroups.MODERATOR, rules.Rights.MIDDLE],
    text=funcs.split_for_text_for_command("Добмод <user> <key:int>"),
)
async def add_moderator(
    message: Message,
    user: str = None,
    key: int = None,
    uow: IUnitOfWork = UOWDep,
) -> None:
    if key is None:
        return await message.answer("Забыл МВ")
    if user is None:
        return await message.answer("Забыл ссылку на страницу!")

    user_info = await vkf.get_user_info(user)

    user_create_schema = user_schema.UserCreateSchema(**user_info.dict())
    stuff_create_schema = stuff_schema.StuffCreateSchema(
        user_id=user_info.id, group_id=rules.StuffGroups.MODERATOR.value, key=key, allowance=1
    )
    stuff_completed_schema = stuff_schema.StuffCompleteCreateSchema(
        user_create_info=user_create_schema, stuff_create_info=stuff_create_schema
    )
    await StuffsService().add_stuff(uow, stuff_completed_schema)
    await message.answer(f"➕ @id{user_info.id} ({user_info.full_name}) добавлен")


@labeler.private_message(
    access=[rules.StuffGroups.MODERATOR, rules.Rights.MIDDLE],
    text=funcs.split_for_text_for_command("Удалмод <user>"),
)
async def delete_moderator(message: Message, user: str = None, uow: IUnitOfWork = UOWDep) -> None:
    if user is None:
        return await message.answer("Нет ссылки на страницу!")

    user_info = await vkf.get_user_info(user)

    stuff = await StuffsService().get_stuff_by(uow, user_id=user_info.id, group_id=rules.StuffGroups.MODERATOR.value)
    stuff_delete_schema = stuff_schema.StuffDeleteSchema(id=stuff.id)
    await StuffsService().delete_stuff(uow, stuff_delete_schema)
    await message.answer(f"➖ @id{user_info.id} ({user_info.full_name}) удалён")


@labeler.private_message(
    access=[rules.StuffGroups.MODERATOR, rules.Rights.MIDDLE],
    text="Модсписок",
)
async def list_moderators(message: Message, uow: IUnitOfWork = UOWDep) -> None:
    service = StuffsService()
    result = await list_stuff_groups(
        uow, stuff_group=rules.StuffGroups.MODERATOR, group_name="Модераторы", service=service
    )
    await message.answer(result)


@labeler.private_message(
    access=[rules.StuffGroups.MODERATOR, rules.Rights.MIDDLE],
    text=funcs.split_for_text_for_command("Добсокр <abbreviation> <full_text>"),
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


@labeler.private_message(
    access=[rules.StuffGroups.MODERATOR, rules.Rights.MIDDLE],
    text=funcs.split_for_text_for_command("Измсокр <abbreviation> <full_text>"),
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


@labeler.private_message(
    access=[rules.StuffGroups.MODERATOR, rules.Rights.MIDDLE],
    text=funcs.split_for_text_for_command("Удалсокр <abbreviation>"),
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
