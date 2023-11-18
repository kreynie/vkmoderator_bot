from abc import abstractmethod
from typing import Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from src.helpfuncs.functions import camel_to_sneak

S = TypeVar("S", bound=BaseModel)


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        return f"{camel_to_sneak(cls.__name__)}s"

    id: Mapped[int] = mapped_column(primary_key=True)

    @abstractmethod
    def to_read_model(self) -> Type[S]:
        ...
