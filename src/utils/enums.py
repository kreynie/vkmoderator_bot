from datetime import datetime
from enum import Enum, IntEnum
from config import chats_id_settings


class Rights(IntEnum):
    ANY = 0
    LOW = 1
    MIDDLE = 2
    LEAD = 3
    ADMIN = 4


class StuffGroups(IntEnum):
    ANY = 0
    MODERATOR = 1
    LEGAL = 2


class SheetsNames(Enum):
    groups = f"Сообщества ({datetime.now():%Y})"
    users = f"Пользователи ({datetime.now():%Y})"


chat_ids = chats_id_settings


class ChatPeers(IntEnum):
    FLOOD = 2000000000 + chat_ids.flood
    VISITING = 2000000000 + chat_ids.visiting
    MODERATORS = 2000000000 + chat_ids.moderators
    NEWS = 2000000000 + chat_ids.news
    HELP_REQUESTS = 2000000000 + chat_ids.help_requests


class ReactionIDs(IntEnum):
    HEART = 1
    FIRE = 2
    LMAO = 3
    THUMB_UP = 4
    POOP = 5
    QUESTION_MARKS = 6
    CRYING = 7
    ANGRY = 8
    THUMB_DOWN = 9
    OK = 10
    SMILING = 11
    THINKING = 12
    FOLDED_HANDS = 13
    KISSING = 14
    HEART_EYES = 15
    CONFETTI = 16
