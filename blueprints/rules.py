from typing import List

from vkbottle.dispatch.rules import ABCRule
from vkbottle.user import Message

from config import legal_db, moderator_db
from utils.enums import Groups, Rights


class PermissionChecker:
    @staticmethod
    async def get_user_permissions(user_id: int, allowance_type: Groups) -> int | bool:
        match allowance_type:
            case Groups.MODERATOR:
                return await moderator_db.get_user_allowance(user_id)
            case Groups.LEGAL:
                return await legal_db.get_user_allowance(user_id)
            case Groups.ANY:
                return any(
                    bool(group)
                    for group in (
                        await moderator_db.get_user_allowance(user_id),
                        await legal_db.get_user_allowance(user_id),
                    )
                )


class CheckPermissions(ABCRule[Message]):
    def __init__(self, data: List[tuple[Groups, Rights | None]]) -> None:
        self.allowance_type, self.level = data

    async def check(self, event: Message) -> bool:
        if self.allowance_type == Groups.ANY:
            return not not await PermissionChecker.get_user_permissions(
                event.from_id, self.allowance_type
            )

        assert isinstance(
            self.level, Rights
        ), "Rights should be defined if not Groups.ANY"

        permissions = await PermissionChecker.get_user_permissions(
            event.from_id,
            self.allowance_type,
        )
        return permissions >= self.level.value
