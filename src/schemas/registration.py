from typing import Literal

from pydantic import BaseModel

from .object_validators import BannerInfo
from .user import UserSchema


class BanRegistrationInfo(BaseModel):
    banner_info: BannerInfo
    user_info: UserSchema
    comment: str
    ban_time: str


class LegalBanRegistrationInfo(BaseModel):
    game: str
    is_group: bool
    moderator_key: str
    reason: str
    screenshot_link: str
    violation_link: str
    violator_link: str
    violator_screen_name: str | None
    dialog_time: str | None = None
    flea: Literal["TRUE", "FALSE"] | None = None
