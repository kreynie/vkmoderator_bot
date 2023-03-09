from typing import Any, Dict, List, Literal, Tuple

from typing_extensions import override
from utils.info_classes import StuffInfo, UserInfo

from .base import Database


class BaseTable(Database):
    TABLE_NAME: str
    COLUMNS: Dict[str, str]
    TRIGGERS: List[Tuple[str, Dict[str, str], str]] | None = None

    def __init__(self, db_file: str) -> None:
        super().__init__(db_file=db_file)
        self.init_database(self.TABLE_NAME, self.COLUMNS)
        if self.TRIGGERS:
            for trigger_name, condition, action in self.TRIGGERS:
                self.create_trigger(self.TABLE_NAME, trigger_name, condition, action)

    async def get_user_by_id(self, user_id: int) -> Dict[str, Any] | None:
        return await self.get_item(self.TABLE_NAME, {"id": user_id})

    async def add_user(self, user_id: int, key: int, allowance: int) -> bool:
        result = await self.add_values(
            self.TABLE_NAME, {"id": user_id, "key": key, "allowance": allowance}
        )
        return True if result > 0 else False

    async def remove_user(self, user_id: int) -> bool:
        result = await self.remove_values(self.TABLE_NAME, {"id": user_id})
        return True if result > 0 else False

    async def edit_user_allowance(self, user_id: int, allowance: int) -> bool:
        result = await self.edit_values(
            self.TABLE_NAME, {"id": user_id}, {"allowance": allowance}
        )
        return True if result > 0 else False

    async def get_user_allowance(self, user_id: int) -> int:
        allowance = await self.get_item(self.TABLE_NAME, {"id": user_id}, "allowance")
        return allowance.get("allowance") if allowance else 0

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
        return UserInfo(
            id=info.get("id"),
            first_name=info.get("first_name"),
            last_name=info.get("last_name"),
        )

    async def get_all(
        self,
        users_group: Literal["moderators", "legal"],
    ) -> List[StuffInfo] | None:
        stuff = await self.get_items(
            self.TABLE_NAME,
            target=f"{self.TABLE_NAME}.id, {self.TABLE_NAME}.first_name, \
                {self.TABLE_NAME}.last_name, {users_group}.key, {users_group}.allowance",
            join_table=users_group,
            join_columns=["key", "allowance"],
            order_by=f"{users_group}.key",
        )
        return [
            StuffInfo(
                person.get("id"),
                person.get("first_name"),
                person.get("last_name"),
                person.get("key"),
                person.get("allowance"),
            )
            for person in stuff
        ]


class StuffTable(BaseTable):
    @override
    async def get_user_by_id(self, user_id: int) -> StuffInfo | None:
        stuff = await super().get_user_by_id(user_id)
        if not stuff:
            return None
        return StuffInfo(
            stuff.get("id"),
            stuff.get("first_name"),
            stuff.get("last_name"),
            stuff.get("key"),
            stuff.get("allowance"),
        )


class _DeleteTriggerLogic:
    BASE_TRIGGER = (
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

    TRIGGERS = [("delete_user_moderator", *_DeleteTriggerLogic.BASE_TRIGGER)]


class LegalTable(StuffTable):
    TABLE_NAME = "legal"
    COLUMNS = {
        "id": "INT",
        "key": "INT NOT NULL",
        "allowance": "INT NOT NULL",
        "FOREIGN KEY (id)": "REFERENCES users(id)",
    }

    TRIGGERS = [("delete_user_legal", *_DeleteTriggerLogic.BASE_TRIGGER)]
