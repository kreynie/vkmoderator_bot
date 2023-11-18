from vkbottle.user import Message

from src.blueprints import rules
from src.helpfuncs import functions as funcs, vkfunctions as vkf
from src.schemas.stuff import StuffUpdatePartialSchema
from src.services.stuffs import StuffsService
from src.utils.dependencies import UOWDep
from src.utils.enums import StuffGroups
from src.utils.exceptions import handle_errors_decorator
from src.utils.unitofwork import IUnitOfWork
from .base_labeler import labeler


@labeler.private_message(
    access=[rules.StuffGroups.ANY, rules.Rights.ADMIN],
    text=funcs.split_for_text_for_command("Права <user> <group:int> <new_allowance:int>"),
)
@handle_errors_decorator()
async def change_rights(
    message: Message,
    user: str = "",
    group: int = 0,
    new_allowance: int = 0,
    uow: IUnitOfWork = UOWDep,
) -> None:
    if not user or not group or not new_allowance:
        return await message.answer("Correct form: Права <user> <group:int> <new_allowance:int>")

    group_id = StuffGroups(group)
    user_info = await vkf.get_user_info(user)

    if group_id not in (StuffGroups.MODERATOR, StuffGroups.LEGAL):
        return await message.answer(f"use mod={StuffGroups.MODERATOR.value} or legal={StuffGroups.LEGAL.value} group")

    stuff = await StuffsService().get_stuff_by(uow, user_id=user_info.id, group_id=group_id.value)
    update_stuff_partial = StuffUpdatePartialSchema(id=stuff.id, allowance=new_allowance)
    await StuffsService().update_stuff(uow, update_stuff_partial, partial=True)
    await message.answer("Succeeded")
