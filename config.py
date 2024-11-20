from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

project_path = Path(__file__).resolve().parent


class BaseEnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=project_path / ".env",
        env_file_encoding="utf-8",
    )


class DBSettings(BaseModel):
    url: str = f"sqlite+aiosqlite:///{project_path / 'db.db'}"
    echo: bool = False


class VKAPISettings(BaseEnvSettings):
    token: str = Field(..., env="VKTOKEN")


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

logger.info(f"Settings loaded: {settings.model_dump()}")

__all__ = (
    "BaseEnvSettings",
    "chats_id_settings",
    "groups_id_settings",
    "logger",
    "project_path",
    "settings",
)
