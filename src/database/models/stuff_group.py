from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from src.schemas.stuff_group import StuffGroup
from .base import Base


if TYPE_CHECKING:
    from .stuff import Stuff


class StuffGroup(Base):
    name: Mapped[str]

    stuffs: Mapped[list["Stuff"]] = relationship(back_populates="group", lazy="immediate")

    def to_read_model(self) -> StuffGroup:
        return StuffGroup.model_validate(self)
