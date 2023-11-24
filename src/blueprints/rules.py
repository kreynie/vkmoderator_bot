from vkbottle.dispatch.rules import ABCRule
from vkbottle.user import Message

from src.utils.dependencies import UOWDep
from src.utils.enums import StuffGroups, Rights
from src.utils.unitofwork import IUnitOfWork
from src.services.stuffs import StuffsService


async def get_user_permissions(
        uow: IUnitOfWork,
        user_id: int,
        allowance_type: StuffGroups,
) -> int:
    if allowance_type == StuffGroups.ANY:
        stuff_accounts = await StuffsService().get_stuffs(uow, user_id=user_id)
        if not stuff_accounts:
            return 0
        highest_allowance = max(stuff_accounts, key=lambda account: account.allowance, default=0)
        return highest_allowance.allowance
    stuff = await StuffsService().get_stuff_by(
        uow, user_id=user_id, group_id=allowance_type.value
    )
    return stuff.allowance if stuff is not None else 0


class CheckPermissions(ABCRule[Message]):
    def __init__(self, data: list[StuffGroups, Rights]) -> None:
        self.allowance_type, self.level = data

    async def check(self, message: Message, uow: IUnitOfWork = UOWDep) -> dict[str, int] | bool:
        max_permissions = await get_user_permissions(uow, message.from_id, StuffGroups.ANY)
        if max_permissions == Rights.ADMIN.value:
            return {"rights": max_permissions}
        permissions = await get_user_permissions(uow, message.from_id, self.allowance_type)
        return permissions >= self.level.value
