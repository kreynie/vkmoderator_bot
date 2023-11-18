from sqlalchemy.orm import Mapped, mapped_column

from src.schemas.hot_issues import HotIssueSchema
from .base import Base


class HotIssue(Base):
    title: Mapped[str] = mapped_column(index=True)
    text: Mapped[str]
    published: Mapped[str] = mapped_column(index=True)

    def to_read_model(self) -> HotIssueSchema:
        return HotIssueSchema.from_orm(self)
