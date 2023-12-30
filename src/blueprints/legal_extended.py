from vkbottle.user import Message

from src.blueprints import rules
from src.helpfuncs import functions as funcs, vkfunctions as vkf
from src.helpfuncs.list_stuffs_utils import list_stuff_groups
from src.schemas import stuff as stuff_schema, user as user_schema
from src.services.stuffs import StuffsService
from src.utils.dependencies import UOWDep
from src.utils.exceptions import handle_errors_decorator
from src.utils.unitofwork import IUnitOfWork
from .base_labeler import labeler


@labeler.private_message(
    access=[rules.StuffGroups.LEGAL, rules.Rights.MIDDLE],
    text=funcs.split_for_text_for_command("ДобЛТ <user> <legal_id:int>"),
)
@handle_errors_decorator()
async def add_legal(
        message: Message,
        uow: IUnitOfWork = UOWDep,
        user: str = "",
        legal_id: int = 0,
) -> None:
    if not legal_id:
        return await message.answer("Забыл айдишник")
    if not user:
        return await message.answer("Забыл ссылку на страницу!")

    user_info = await vkf.get_user_info(user)

    stuff_create_schema = stuff_schema.StuffCreateSchema(
        user_id=user_info.id, group_id=rules.StuffGroups.LEGAL.value, key=legal_id, allowance=1
    )
    stuff_completed_schema = stuff_schema.StuffCompleteCreateSchema(
        user_create_info=user_schema.UserCreateSchema(**user_info.dict()),
        stuff_create_info=stuff_create_schema
    )
    await StuffsService().add_stuff(uow, stuff_completed_schema)
    await message.answer(f"➕ @id{user_info.id} ({user_info.full_name}) добавлен")


@labeler.private_message(
    access=[rules.StuffGroups.LEGAL, rules.Rights.MIDDLE],
    text=funcs.split_for_text_for_command("УдалЛТ <user>"),
)
@handle_errors_decorator()
async def remove_legal(
        message: Message,
        uow: IUnitOfWork = UOWDep,
        user: str = "",
) -> None:
    if not user:
        await message.answer("Забыл ссылку на страницу!")
        return

    user_info = await vkf.get_user_info(user)

    stuff = await StuffsService().get_stuff_by(uow, user_id=user_info.id, group_id=rules.StuffGroups.LEGAL.value)
    delete_stuff_schema = stuff_schema.StuffDeleteSchema(
        id=stuff.id, user_id=user_info.id, group_id=rules.StuffGroups.LEGAL.value
    )
    await StuffsService().delete_stuff(uow, delete_stuff_schema)
    await message.answer(f"➖ @id{user_info.id} ({user_info.full_name}) удалён")


@labeler.private_message(
    access=[rules.StuffGroups.LEGAL, rules.Rights.MIDDLE],
    text="ЛТсписок",
)
async def list_legal(message: Message, uow: IUnitOfWork = UOWDep) -> None:
    service = StuffsService()
    result = await list_stuff_groups(
        uow, stuff_group=rules.StuffGroups.LEGAL, group_name="LT", service=service
    )
    await message.answer(result)
