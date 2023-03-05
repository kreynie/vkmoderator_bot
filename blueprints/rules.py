from typing import List

from config import legal_db, moderator_db
from vkbottle.dispatch.rules import ABCRule
from vkbottle.user import Message

from .enums import Groups, Rights


class PermissionChecker:
    @classmethod
    async def get_user_permissions(cls, user_id: int, allowance_type: Groups) -> int:
        match allowance_type:
            case Groups.MODERATOR:
                return await moderator_db.get_user_allowance(user_id)
            case Groups.LEGAL:
                return await legal_db.get_user_allowance(user_id)


class CheckPermissions(ABCRule[Message]):
    def __init__(self, data: List[tuple[Groups, Rights]]) -> None:
        self.allowance_type, self.level = data

    async def check(self, event: Message) -> bool:
        permissions = await PermissionChecker.get_user_permissions(
            event.from_id,
            self.allowance_type,
        )
        return permissions >= self.level.value
