from dataclasses import dataclass, field


@dataclass
class UserInfo:
    id: int
    first_name: str
    last_name: str
    full_name: str = field(init=False)

    def __post_init__(self) -> None:
        self.full_name = f"{self.first_name} {self.last_name}"


@dataclass
class StuffInfo(UserInfo):
    key: int
    allowance: int
