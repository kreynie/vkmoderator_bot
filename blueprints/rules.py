from typing import List

from vkbottle.dispatch.rules import ABCRule
from vkbottle.user import Message

from helpfuncs.jsonfunctions import DictionaryFuncs, JSONHandler

from .enums import Groups, Rights

json_handler = JSONHandler()
dict_handler = DictionaryFuncs()


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
    def __init__(self, data: List[tuple[Groups, Rights]]) -> None:
        self.permission_type, self.level = data

    async def check(self, event: Message) -> bool:
        permissions = await PermissionChecker.get_user_permissions(
            str(event.from_id), self.permission_type
        )
        return permissions >= self.level.value
