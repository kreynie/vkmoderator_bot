from pydantic import BaseModel
from vkbottle_types.codegen.objects import GroupsGroupFull, UsersUserFull

from .stuff import StuffSchema


class VKObjectInfo(BaseModel):
    object: GroupsGroupFull | UsersUserFull
    is_group: bool


class BannerInfo(BaseModel):
    moderator: StuffSchema
    key: str
