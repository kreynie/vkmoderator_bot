from enum import Enum
from vkbottle.dispatch.rules import ABCRule
from vkbottle.user import Message

from helpfuncs.jsonfunctions import JSONHandler


json_handler = JSONHandler()


class Rights(Enum):
    moderator = 1
    supermoderator = 2
    lead = 3
    admin = 4


async def get_user_permissions(user_id: str, flag: str = None) -> int:
    moderators = json_handler.get_data()
    if user_id in moderators and flag:
        return moderators[user_id].get(flag, 1)
    return 0


async def check_permissions(user_permissions: int, access_level: int) -> bool:
    if access_level:
        return user_permissions >= access_level


class CheckRights(ABCRule[Message]):
    def __init__(self, level: int) -> None:
        self.level = level

    async def check(self, event: Message) -> bool:
        rights = await get_user_permissions(str(event.from_id), "rights")
        permissions = await check_permissions(rights, self.level.value)
        return permissions


class Groups(Enum):
    moderator = 1
    legal = 2


class CheckGroups(ABCRule[Message]):
    def __init__(self, group: str) -> None:
        self.group = group

    async def check(self, event: Message) -> bool:
        groups = get_user_permissions(str(event.from_id), "groups")
        rights = rights[str(event.from_id)].get(groups, Groups.moderator.value)
        return rights >= Groups.legal.value
