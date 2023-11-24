from pathlib import Path

from loguru import logger
from pydantic import BaseSettings, Field

project_path = Path(__file__).resolve().parent


class BaseEnvSettings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class DBSettings(BaseSettings):
    url: str = f"sqlite+aiosqlite:///{project_path / 'db.db'}"
    echo: bool = False


class VKAPISettings(BaseEnvSettings):
    token: str = Field(..., env="VKTOKEN")


class GoogleSettings(BaseEnvSettings):
    credentials_path: Path = project_path / "creds.json"
    spreadsheet: str = Field("1_QwV3b-ue0xG3McMLjO6rijjuaVP8VBhD-G1x2kOW7s", env="SPREADSHEET")


class ChatsIDSettings(BaseEnvSettings):
    flood: int = Field(..., env="CHAT_ID_FLOOD")
    visiting: int = Field(..., env="CHAT_ID_VISITING")
    moderators: int = Field(..., env="CHAT_ID_MODERATORS")
    news: int = Field(..., env="CHAT_ID_NEWS")
    help_requests: int = Field(..., env="CHAT_ID_HELP_REQUESTS")


class GroupsIDSettings(BaseEnvSettings):
    main_group: int = Field(-200352287, env="MAIN_GROUP")
    ban_archive_group: int = Field(-200352287, env="BAN_ARCHIVE_GROUP")


class Settings(BaseEnvSettings):
    db: DBSettings = DBSettings()
    vk_api: VKAPISettings = VKAPISettings()
    google_api: GoogleSettings = GoogleSettings()
    debug: bool = Field(False, env="DEBUG")


chats_id_settings: ChatsIDSettings = ChatsIDSettings()
groups_id_settings: GroupsIDSettings = GroupsIDSettings()
settings: Settings = Settings()


logger.remove()
logger.add(
    project_path / "debug.log",
    format="{time} {level} {message}",
    level="INFO",
    backtrace=True,
    catch=True,
    rotation="00:00",
    retention=1,
    compression="zip",
)

if settings.debug:
    import sys
    logger.add(
        sys.stdout,
        format="{time} {level} {message}",
        level="DEBUG",
        colorize=True,
    )


__all__ = (
    "BaseEnvSettings",
    "chats_id_settings",
    "groups_id_settings",
    "logger",
    "project_path",
    "settings",
)
