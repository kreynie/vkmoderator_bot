import abc

from src.repositories.hot_issues import HotIssuesRepository
from src.repositories.stuffs import StuffsRepository
from src.repositories.users import UsersRepository
from src.database import db_helper


class IUnitOfWork(abc.ABC):
    users: UsersRepository
    stuffs: StuffsRepository
    hot_issues: HotIssuesRepository

    @abc.abstractmethod
    def __init__(self):
        ...

    @abc.abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        ...

    @abc.abstractmethod
    async def __aexit__(self, *args) -> None:
        ...

    @abc.abstractmethod
    async def commit(self) -> None:
        ...

    @abc.abstractmethod
    async def rollback(self) -> None:
        ...


class UnitOfWork(IUnitOfWork):
    def __init__(self):
        self.session_factory = db_helper.session_factory

    async def __aenter__(self) -> "UnitOfWork":
        self.session = self.session_factory()

        self.users = UsersRepository(self.session)
        self.stuffs = StuffsRepository(self.session)
        self.hot_issues = HotIssuesRepository(self.session)

        return self

    async def __aexit__(self, *args) -> None:
        await self.rollback()
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
