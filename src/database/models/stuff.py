from typing import TYPE_CHECKING

from sqlalchemy import Connection, delete, event, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session

from src.schemas.stuff import Stuff as StuffSchema
from .base import Base
from .mixins import ProvidesUserMixin
from .user import User

if TYPE_CHECKING:
    from .stuff_group import StuffGroup


class Stuff(ProvidesUserMixin, Base):
    __table_args__ = (
        UniqueConstraint("user_id", "group_id", "key", name="uix_stuff_account"),
    )
    _user_back_populates = "stuff_accounts"

    group_id: Mapped[int] = mapped_column(ForeignKey("stuff_groups.id"))
    key: Mapped[int]
    allowance: Mapped[int] = mapped_column(default=1)

    group: Mapped["StuffGroup"] = relationship(back_populates="stuffs", lazy="immediate")

    def to_read_model(self) -> StuffSchema:
        return StuffSchema.model_validate(self)


@event.listens_for(Stuff, "after_delete")
def delete_user_if_no_stuff(mapper, connection: Connection, target) -> None:
    """Delete user if last stuff account is going to be deleted."""
    selected_user: User = target.user
    if len(selected_user.stuff_accounts) == 1:
        session = Session(bind=connection)
        stmt = delete(User).where(User.id == selected_user.id)
        session.execute(stmt)
        session.commit()
