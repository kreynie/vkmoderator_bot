from pydantic import BaseModel

from .object_validators import BannerInfo
from .user import UserSchema


class BanRegistrationInfo(BaseModel):
    banner_info: BannerInfo
    user_info: UserSchema
    comment: str
    ban_time: str
