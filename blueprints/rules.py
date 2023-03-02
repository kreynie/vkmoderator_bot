from enum import Enum
from typing import List

from vkbottle.dispatch.rules import ABCRule
from vkbottle.user import Message

from helpfuncs.jsonfunctions import DictionaryFuncs, JSONHandler

json_handler = JSONHandler()
dict_handler = DictionaryFuncs()


class Rights(Enum):
    LOW = 1
    MIDDLE = 2
    LEAD = 3
    ADMIN = 4


class Groups(Enum):
    MODERATOR = "groups.moderator"
    LEGAL = "groups.legal"


class PermissionChecker:
    @classmethod
    async def get_user_permissions(cls, user_id: str, permission_type: Groups) -> int:
        moderators = json_handler.get_data()
        return await dict_handler.get_value_by_key_path(
            dictionary=moderators,
            path=f"{user_id}.{permission_type.value}",
            default=0,
        )


class CheckPermissions(ABCRule[Message]):
    def __init__(self, data: List[Groups, Rights]) -> None:
        self.permission_type, self.level = data

    async def check(self, event: Message) -> bool:
        permissions = await PermissionChecker.get_user_permissions(
            str(event.from_id), self.permission_type
        )
        return permissions >= self.level.value
