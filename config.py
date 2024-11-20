from pathlib import Path

from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

project_path = Path(__file__).resolve().parent


class BaseEnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=project_path / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class DBSettings(BaseSettings):
    url: str = f"sqlite+aiosqlite:///{project_path / 'db.db'}"
    echo: bool = False


class VKAPISettings(BaseEnvSettings):
    token: str = Field(..., alias="VKTOKEN")


class ChatsIDSettings(BaseSettings):
    flood: int
    visiting: int
    moderators: int
    news: int
    help_requests: int

    model_config = SettingsConfigDict(
        env_file=project_path / ".env",
        env_file_encoding="utf-8",
        env_prefix="CHAT_ID_",
        extra="ignore",
    )


class GroupsIDSettings(BaseEnvSettings):
    main_group: int = Field(-200352287, alias="MAIN_GROUP")
    ban_archive_group: int = Field(-200352287, alias="BAN_ARCHIVE_GROUP")


class Settings(BaseEnvSettings):
    db: DBSettings = DBSettings()
    vk_api: VKAPISettings = VKAPISettings()
    debug: bool = Field(False, alias="DEBUG")


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

logger.info(f"Settings loaded: {settings.model_dump()}")

__all__ = (
    "chats_id_settings",
    "groups_id_settings",
    "logger",
    "project_path",
    "settings",
)
