from dataclasses import dataclass

from pydantic import BaseModel
from vkbottle_types.codegen.objects import GroupsGroupFull, UsersUserFull

from .stuff import StuffSchema
from .user import UserSchema


@dataclass
class VKObjectInfo:
    object: GroupsGroupFull | UsersUserFull | UserSchema
    is_group: bool


class BannerInfo(BaseModel):
    moderator: StuffSchema
    key: str
