from src.database.models.hot_issues import HotIssue
from src.utils.repository import SQLAlchemyRepository


class HotIssuesRepository(SQLAlchemyRepository):
    model = HotIssue
