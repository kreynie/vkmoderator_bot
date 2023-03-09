from enum import Enum


class Rights(Enum):
    ANY = 0
    LOW = 1
    MIDDLE = 2
    LEAD = 3
    ADMIN = 4


class Groups(Enum):
    ANY = 0
    MODERATOR = 1
    LEGAL = 2
