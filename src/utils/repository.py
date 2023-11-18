import abc
from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy import and_, ColumnElement, insert, Result, select, update
from sqlalchemy import exc as sa_exc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import exceptions as db_exc
from src.database.models import Base

K = TypeVar("K")
M = TypeVar("M", bound=Base)
S = TypeVar("S", bound=BaseModel)


class AbstractRepository(abc.ABC):
    model: K

    @abc.abstractmethod
    async def add_one(self, data: dict) -> K:
        raise NotImplementedError

    @abc.abstractmethod
    async def find_one(self, **filter_by) -> K | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def find_all(self) -> list[K]:
        raise NotImplementedError

    @abc.abstractmethod
    async def update_one(self, data: dict, **filter_by) -> K | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_one(self, **filter_by) -> None:
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    """Implementation of the Abstract Repository for SQLAlchemy"""
    model: M

    def __init__(self, session: AsyncSession):
        """
        Initialize the SQLAlchemyRepository.

        :param session: An asynchronous SQLAlchemy session.
        """
        self.session: AsyncSession = session

    async def add_one(self, data: dict) -> S:
        """
        Add one row to the table.

        :param data: Values to be added.
        :return: The added row as model's schema.
        """
        try:
            stmt = insert(self.model).values(**data).returning(self.model)
            res: Result = await self.session.execute(stmt)
            return res.scalar_one().to_read_model()
        except sa_exc.IntegrityError as e:
            raise db_exc.EntityAlreadyExists(f"Entity with provided data already exists: {data}") from e
        except sa_exc.SQLAlchemyError as e:
            raise db_exc.DatabaseException from e

    async def find_one(self, **filter_by) -> S | None:
        """
        Find one row in the table.

        :param filter_by: Filter criteria.
        :return: The found row as model's schema or None if not found.
        """
        try:
            filter_clause = self._build_filter(**filter_by)
            stmt = select(self.model).where(filter_clause)
            return await self._execute_and_return_one(stmt)
        except sa_exc.NoResultFound as e:
            raise db_exc.EntityDoesNotExist(f"Entity with provided filter {filter_by} does not exist") from e
        except sa_exc.MultipleResultsFound as e:
            raise db_exc.MultipleEntityFound from e
        except sa_exc.SQLAlchemyError as e:
            raise db_exc.DatabaseException from e

    async def find_last(self) -> S | None:
        """
        Find last row in the table.

        :return:
        """
        try:
            stmt = select(self.model).order_by(self.model.id.desc()).limit(1)
            return await self._execute_and_return_one(stmt)
        except sa_exc.SQLAlchemyError as e:
            raise db_exc.DatabaseException from e

    async def find_all(self, limit: int = None, offset: int = None, **filter_by) -> list[S]:
        """
        Find all rows in the table.

        :return: List of all rows as model's schemas or empty list if no rows found.
        """
        try:
            filter_clause = self._build_filter(**filter_by)
            stmt = select(self.model).where(filter_clause).offset(offset).limit(limit)
            return await self._execute_and_return_all(stmt)
        except sa_exc.NoResultFound as e:
            raise db_exc.EntityDoesNotExist(f"No result found with such criteria: {filter_by}") from e
        except sa_exc.SQLAlchemyError as e:
            raise db_exc.DatabaseException from e

    async def _execute_and_return_one(self, stmt) -> S | None:
        res: Result = await self.session.execute(stmt)
        returned_model = res.scalar_one_or_none()
        return returned_model.to_read_model() if returned_model is not None else None

    async def _execute_and_return_all(self, stmt) -> list[S]:
        res: Result = await self.session.execute(stmt)
        returned_models = res.scalars().all()
        return [returned_model.to_read_model() for returned_model in returned_models]

    async def update_one(self, data: dict, **filter_by) -> S | None:
        """
        Update one row in the table.

        :param data: Values to be updated.
        :param filter_by: Filter criteria.
        :return: The updated row as model's schema.
        """
        try:
            filter_clause = self._build_filter(**filter_by)
            stmt = update(self.model).values(**data).where(filter_clause).returning(self.model)
            res: Result = await self.session.execute(stmt)
            returned_model = res.scalar_one()
            return returned_model.to_read_model()
        except sa_exc.NoResultFound as e:
            raise db_exc.EntityDoesNotExist(f"No result found with such criteria: {filter_by}") from e
        except sa_exc.SQLAlchemyError as e:
            raise db_exc.DatabaseException from e

    async def delete_one(self, **filter_by) -> None:
        """
        Delete one row from the table.

        :param filter_by: Filter criteria.
        """
        # This workaround correctly loads models' relationships
        try:
            filter_clause = self._build_filter(**filter_by)
            stmt = select(self.model).where(filter_clause)
            res: Result = await self.session.execute(stmt)
            obj: Result = res.scalar_one()
            await self.session.delete(obj)
        except sa_exc.NoResultFound as e:
            raise db_exc.EntityDoesNotExist(f"No result found with such criteria: {filter_by}") from e
        except sa_exc.SQLAlchemyError as e:
            raise db_exc.DatabaseException from e

    def _build_filter(self, **kwargs) -> ColumnElement[bool]:
        filter_clauses = []

        operators = {
            "__ne": lambda col, val: col != val,
            "__lt": lambda col, val: col < val,
            "__gt": lambda col, val: col > val,
            "__lte": lambda col, val: col <= val,
            "__gte": lambda col, val: col >= val,
            "__in": lambda col, val: col.in_(val),
            "__not_in": lambda col, val: col.not_in(val),
            "__like": lambda col, val: col.like(val),
        }

        for key, value in kwargs.items():
            for op, op_func in operators.items():
                if op in key:
                    column_name = key.replace(op, "")
                    filter_clauses.append(op_func(getattr(self.model, column_name), value))
                    break
            else:
                filter_clauses.append(getattr(self.model, key) == value)

        return and_(*filter_clauses)
