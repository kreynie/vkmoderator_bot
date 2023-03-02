from enum import Enum


class Rights(Enum):
    LOW = 1
    MIDDLE = 2
    LEAD = 3
    ADMIN = 4


class Groups(Enum):
    MODERATOR = "groups.moderator"
    LEGAL = "groups.legal"
