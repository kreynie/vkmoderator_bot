from typing import Optional

from pydantic.dataclasses import dataclass


@dataclass
class UserInfo:
    id_: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    screen_name: Optional[str] = None

    def __post_init__(self) -> None:
        if self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}"


@dataclass
class StuffInfo(UserInfo):
    key: int = 0
    allowance: int = 0


@dataclass
class GroupInfo:
    id_: int
    screen_name: Optional[str] = None
