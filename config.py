from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from vkbottle import API
from vkbottle.user import UserLabeler

from database import LegalTable, ModeratorTable, UsersTable

project_path = Path(__file__).resolve().parent

load_dotenv()
DEBUG = getenv("DEBUG", 0)

# VK
token = getenv("VKToken")
api = API(token=token)

# Google API
spreadsheet = (
    "1_QwV3b-ue0xG3McMLjO6rijjuaVP8VBhD-G1x2kOW7s" if DEBUG else getenv("spreadsheet")
)
credentials_path = project_path / "creds.json"

labeler = UserLabeler()

db_file_name = project_path / "base.db"
users_db = UsersTable(db_file_name)
moderator_db = ModeratorTable(db_file_name)
legal_db = LegalTable(db_file_name)

if DEBUG:
    ban_group_id, ban_reason_group_id = -200352287, -200352287
else:
    ban_group_id, ban_reason_group_id = -49033185, -112433737


logger.remove()
logger.add(
    project_path / "debug.log",
    format="{time} {level} {message}",
    level="DEBUG" if DEBUG else "INFO",
    rotation="00:00",
    retention=1,
    compression="zip",
)


__all__ = (
    "api",
    "ban_group_id",
    "ban_reason_group_id",
    "credentials_path",
    "labeler",
    "legal_db",
    "moderator_db",
    "project_path",
    "spreadsheet",
    "users_db",
)
