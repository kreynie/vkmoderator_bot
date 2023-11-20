from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import declared_attr, mapped_column, relationship, Mapped


if TYPE_CHECKING:
    from .user import User


class ProvidesUserMixin:
    _user_back_populates: str | None = None

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    @declared_attr
    @classmethod
    def user(cls) -> Mapped["User"]:
        return relationship(back_populates=cls._user_back_populates, lazy="immediate")
