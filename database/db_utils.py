from typing import Any, Dict, List, Literal, Tuple

from typing_extensions import override

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

    async def get_user_by_id(self, id: int) -> Dict[str, Any]:
        return await self.get_item(self.TABLE_NAME, {"id": id})

    async def add_user(self, id: int, key: int, allowance: int) -> bool:
        result = await self.add_values(
            self.TABLE_NAME, {"id": id, "key": key, "allowance": allowance}
        )
        return True if result > 0 else False

    async def remove_user(self, id: int) -> bool:
        result = await self.remove_values(self.TABLE_NAME, {"id": id})
        return True if result > 0 else False

    async def edit_user_allowance(self, id: int, allowance: int) -> bool:
        result = await self.edit_values(
            self.TABLE_NAME, {"id": id}, {"allowance": allowance}
        )
        return True if result > 0 else False

    async def get_user_allowance(self, id: int) -> int:
        allowance = await self.get_item(self.TABLE_NAME, {"id": id}, "allowance")
        return allowance.get("allowance") if allowance else 0

    async def has_user(self, id: int) -> bool:
        return not not await self.get_user_by_id(id)

    async def get_all(
        self,
        users_group: Literal["moderators", "legal"],
    ) -> List[Dict[str, Any]] | None:
        return await self.get_items(
            "users",
            target=f"users.id, users.first_name, users.last_name, \
                {users_group}.key, {users_group}.allowance",
            join_table=users_group,
            join_columns=["key", "allowance"],
            order_by=f"{users_group}.key",
        )


class UsersTable(BaseTable):
    TABLE_NAME = "users"
    COLUMNS = {
        "id": "INT UNIQUE PRIMARY KEY NOT NULL",
        "first_name": "TEXT NOT NULL",
        "last_name": "TEXT NOT NULL",
    }

    @override
    async def add_user(self, id: int, first_name: str, last_name: str) -> bool:
        result = await self.add_values(
            self.TABLE_NAME,
            {"id": id, "first_name": first_name, "last_name": last_name},
        )
        return result


class ModeratorTable(BaseTable):
    TABLE_NAME = "moderators"
    COLUMNS = {
        "id": "INT",
        "key": "INT NOT NULL",
        "allowance": "INT NOT NULL",
        "FOREIGN KEY (id)": "REFERENCES users(id)",
    }

    TRIGGERS = [
        (
            "delete_user_moderator",
            {"moderators": "id = OLD.id", "legal": "id = OLD.id"},
            "DELETE FROM users WHERE id = OLD.id",
        )
    ]


class LegalTable(BaseTable):
    TABLE_NAME = "legal"
    COLUMNS = {
        "id": "INT",
        "key": "INT NOT NULL",
        "allowance": "INT NOT NULL",
        "FOREIGN KEY (id)": "REFERENCES users(id)",
    }

    TRIGGERS = [
        (
            "delete_user_legal",
            {"moderators": "id = OLD.id", "legal": "id = OLD.id"},
            "DELETE FROM users WHERE id = OLD.id",
        )
    ]
