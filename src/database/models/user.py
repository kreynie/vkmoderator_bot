from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from src.schemas.user import User as UserSchema
from .base import Base

if TYPE_CHECKING:
    from .stuff import Stuff


class User(Base):
    first_name: Mapped[str]
    last_name: Mapped[str]

    stuff_accounts: Mapped[list["Stuff"]] = relationship(
        "Stuff",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="immediate",
    )

    def to_read_model(self) -> UserSchema:
        return UserSchema.model_validate(self)
