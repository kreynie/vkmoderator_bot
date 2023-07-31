import sqlite3
from typing import Any, Literal

import aiosqlite


class Database:
    """
    Parent class for all databases

    Call init.database() in class __init__ function initialize databases.
    That function will create new tables with their columns and column
    types if they are not exist.
    """

    def __init__(self, db_file: str) -> None:
        self._db_file = db_file

    def init_database(self, table_name: str, columns: dict) -> None:
        """Creates necessary table if not exists

        :param table_name: name of table
        :type table_name: str
        :param columns: creates columns with their names and types
        :type columns: dict
        """
        with sqlite3.connect(self._db_file) as db:
            db.execute("PRAGMA foreign_keys = ON")
            column_defs = ", ".join(
                f"{col_name} {col_type}" for col_name, col_type in columns.items()
            )
            db.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs})")

    async def create_indexes(self, table_name: str, indexes: list) -> None:
        async with aiosqlite.connect(self._db_file) as db:
            for index_def in indexes:
                await db.execute(
                    f"CREATE INDEX IF NOT EXISTS \
                    {table_name}_{index_def} ON {table_name} ({index_def})"
                )

            await db.commit()

    def create_trigger(
        self,
        table_name: str,
        trigger_name: str,
        conditions: dict[str, str],
        action: str,
        event: bool = True,
    ) -> None:
        """Creates trigger for the table

        :param table_name: name of wanted table
        :type table_name: str
        :param trigger_name: unique trigger name
        :type trigger_name: str
        :param conditions: conditions when trigger will work
        :type conditions: Dict[str, str]
        :param action: what trigger should do
        :type action: str
        :param event: AFTER DELETE or BEFORE INSERT accordingly, defaults to True
        :type event: bool, optional
        """
        with sqlite3.connect(self._db_file) as db:
            trigger_type = "AFTER DELETE" if event else "BEFORE INSERT"
            conditions_str = " AND ".join(
                [
                    f"NOT EXISTS (SELECT 1 FROM {table} WHERE {condition})"
                    for table, condition in conditions.items()
                ]
            )
            sql_query = f"""CREATE TRIGGER IF NOT EXISTS {trigger_name}
                            {trigger_type} ON {table_name}
                            WHEN {conditions_str}
                            BEGIN
                                {action};
                            END;"""
            db.execute(sql_query)
            db.commit()

    async def add_values(self, table_name: str, values: dict[str, Any]) -> int:
        async with aiosqlite.connect(self._db_file) as db:
            placeholders = ", ".join("?" for _ in values.values())
            columns = ", ".join(values.keys())
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            result = await db.execute(query, tuple(values.values()))
            await db.commit()
            return result.rowcount

    async def remove_values(self, table_name: str, conditions: dict[str, Any]) -> int:
        async with aiosqlite.connect(self._db_file) as db:
            query = f"DELETE FROM {table_name} WHERE {', '.join(f'{k} = ?' for k in conditions)}"
            values = tuple(conditions.values())
            result = await db.execute(query, values)
            await db.commit()
            return result.rowcount

    async def edit_values(
        self,
        table_name: str,
        condition: dict[str, Any],
        update_values: dict[str, Any],
    ) -> int:
        async with aiosqlite.connect(self._db_file) as db:
            set_clause = ", ".join([f"{col} = ?" for col in update_values.keys()])
            where_clause = " AND ".join([f"{col} = ?" for col in condition.keys()])
            values = tuple(list(update_values.values()) + list(condition.values()))
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            result = await db.execute(query, values)
            await db.commit()
            return result.rowcount

    async def get_item(
        self,
        table_name: str,
        condition: dict[str, Any] = None,
        target: str = "*",
        join_table: str = None,
        join_columns: list[str] = None,
    ) -> dict[str, Any] | None:
        async with aiosqlite.connect(self._db_file) as db:
            query = f"SELECT {target} FROM {table_name}"
            if join_table and join_columns:
                join_clause = (
                    f" INNER JOIN {join_table} ON {table_name}.id={join_table}.id"
                )
                query += join_clause
                target += (
                    f", {', '.join([f'{join_table}.{col}' for col in join_columns])}"
                )
            if condition:
                query += " WHERE " + " AND ".join([f"{k} = ?" for k in condition])
            async with db.execute(
                query, tuple(condition.values()) if condition else None
            ) as cursor:
                result = await cursor.fetchone()
                if not result:
                    return None
                columns = [d[0] for d in cursor.description]
                return dict(zip(columns, result))

    async def get_items(
        self,
        table_name: str,
        condition: dict[str, Any] = None,
        target: str = "*",
        order_by: str = None,
        order_direction: Literal["ASC", "DESC"] = None,
        join_table: str = None,
        join_columns: list[str] = None,
    ) -> list[dict[str, Any]] | None:
        async with aiosqlite.connect(self._db_file) as db:
            query = f"SELECT {target} FROM {table_name}"
            if join_table and join_columns:
                join_clause = (
                    f" INNER JOIN {join_table} ON {table_name}.id={join_table}.id"
                )
                query += join_clause
                target += (
                    f", {', '.join([f'{join_table}.{col}' for col in join_columns])}"
                )
            if condition:
                query += " WHERE " + " AND ".join([f"{k} = ?" for k in condition])
            if order_by:
                query += f" ORDER BY {order_by}"
            if order_by and order_direction:
                query += f" {order_direction}"
            async with db.execute(
                query, tuple(condition.values()) if condition else None
            ) as cursor:
                result = await cursor.fetchall()
                if not result:
                    return None
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in result]
