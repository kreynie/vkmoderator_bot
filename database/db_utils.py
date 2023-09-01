from typing import Any, Literal, Optional

from typing_extensions import override
from utils.info_classes import StuffInfo, UserInfo

from .base import Database


class BaseTable(Database):
    TABLE_NAME: str
    COLUMNS: dict[str, str]
    TRIGGERS: list[tuple[str, dict[str, str], str]] | None = None

    def __init__(self, db_file: str) -> None:
        super().__init__(db_file=db_file)
        self.init_database(self.TABLE_NAME, self.COLUMNS)
        if self.TRIGGERS:
            for trigger_name, condition, action in self.TRIGGERS:
                self.create_trigger(self.TABLE_NAME, trigger_name, condition, action)

    async def get_user_by_id(
        self,
        user_id: int,
        group: Optional[Literal["users", "moderators", "legal"]] = None,
    ) -> dict[str, Any] | None:
        return await self.get_item(self.TABLE_NAME, {"id": user_id}, join_table=group)

    async def add_user(self, user_id: int, key: int, allowance: int) -> bool:
        result = await self.add_values(
            self.TABLE_NAME, {"id": user_id, "key": key, "allowance": allowance}
        )
        return True if result > 0 else False

    async def remove_user(self, user_id: int) -> bool:
        result = await self.remove_values(self.TABLE_NAME, {"id": user_id})
        return True if result > 0 else False

    async def has_user(self, user_id: int) -> bool:
        return not not await self.get_user_by_id(user_id)


class UsersTable(BaseTable):
    TABLE_NAME = "users"
    COLUMNS = {
        "id": "INT UNIQUE PRIMARY KEY NOT NULL",
        "first_name": "TEXT NOT NULL",
        "last_name": "TEXT NOT NULL",
    }

    @override
    async def add_user(self, user_id: int, first_name: str, last_name: str) -> bool:
        result = await self.add_values(
            self.TABLE_NAME,
            {"id": user_id, "first_name": first_name, "last_name": last_name},
        )
        return not not result

    @override
    async def get_user_by_id(self, user_id: int) -> UserInfo | None:
        info = await super().get_user_by_id(user_id)
        if not info:
            return None
        return UserInfo(**info)


class StuffTable(BaseTable):
    @override
    async def get_user_by_id(self, user_id: int) -> StuffInfo | None:
        stuff = await super().get_user_by_id(user_id, UsersTable.TABLE_NAME)
        if not stuff:
            return None
        return StuffInfo(**stuff)

    async def get_all(
        self,
        *,
        condition: Optional[dict[str]] = None,
        order_by: Optional[str] = None,
        order_direction: Literal["ASC", "DESC"] = None,
    ) -> list[StuffInfo] | None:
        if not order_by:
            order_by = f"{self.TABLE_NAME}.key"
        stuff = await self.get_items(
            self.TABLE_NAME,
            condition=condition,
            target=f"{UsersTable.TABLE_NAME}.id, {UsersTable.TABLE_NAME}.first_name, \
                {UsersTable.TABLE_NAME}.last_name, {self.TABLE_NAME}.key, {self.TABLE_NAME}.allowance",
            order_by=order_by,
            order_direction=order_direction,
            join_table=UsersTable.TABLE_NAME,
            join_columns=["id", "first_name", "last_name"],
        )
        return [StuffInfo(**person) for person in stuff]

    async def edit_user_allowance(self, user_id: int, allowance: int) -> bool:
        result = await self.edit_values(
            self.TABLE_NAME, {"id": user_id}, {"allowance": allowance}
        )
        return True if result > 0 else False

    async def get_user_allowance(self, user_id: int) -> int:
        allowance = await self.get_item(self.TABLE_NAME, {"id": user_id}, "allowance")
        return allowance.get("allowance") if allowance else 0


BASE_DELETING_TRIGGER = (
    {"moderators": "id = OLD.id", "legal": "id = OLD.id"},
    "DELETE FROM users WHERE id = OLD.id",
)


class ModeratorTable(StuffTable):
    TABLE_NAME = "moderators"
    COLUMNS = {
        "id": "INT",
        "key": "INT NOT NULL",
        "allowance": "INT NOT NULL",
        "FOREIGN KEY (id)": "REFERENCES users(id)",
    }

    TRIGGERS = [("delete_user_moderator", *BASE_DELETING_TRIGGER)]


class LegalTable(StuffTable):
    TABLE_NAME = "legal"
    COLUMNS = {
        "id": "INT",
        "key": "INT NOT NULL",
        "allowance": "INT NOT NULL",
        "FOREIGN KEY (id)": "REFERENCES users(id)",
    }

    TRIGGERS = [("delete_user_legal", *BASE_DELETING_TRIGGER)]
