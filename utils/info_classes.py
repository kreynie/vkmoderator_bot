from typing import Literal

from pydantic.dataclasses import dataclass


@dataclass
class UserInfo:
    id: int
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    screen_name: str | None = None

    def __post_init__(self) -> None:
        if self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}"


@dataclass
class StuffInfo(UserInfo):
    key: int = 0
    allowance: int = 0


@dataclass
class GroupInfo:
    id: int
    screen_name: str | None = None


@dataclass
class ObjectInfo:
    object: UserInfo | GroupInfo
    is_group: bool


@dataclass
class BannerInfo:
    moderator: StuffInfo
    key: str


@dataclass
class BanRegistrationInfo:
    banner_info: BannerInfo
    user_info: UserInfo
    comment: str
    ban_time: str


@dataclass
class LegalBanRegistrationInfo:
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
