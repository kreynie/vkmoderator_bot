from src.schemas.hot_issues import HotIssueSchema, HotIssuesResponseModel
from src.services.hot_issues import HotIssuesService
from src.utils.dependencies import UOWDep
from src.utils.unitofwork import IUnitOfWork
from config import logger


class HotIssuesProcessor:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow
        self._hot_issues_service = HotIssuesService()

    async def process_issues(self, issues: HotIssuesResponseModel) -> HotIssueSchema | None:
        latest_issue = issues.data[0]
        issue_details = latest_issue.translations.data[0]  # get only first translation version
        issue_schema = HotIssueSchema(
            id=latest_issue.id,
            title=issue_details.title,
            text=issue_details.text,
            published=latest_issue.published,
        )
        issue_in_db = await self._hot_issues_service.get_issue_by(self._uow, id=issue_schema.id)
        if issue_in_db is not None and issue_schema.published == issue_in_db.published:
            return logger.debug(f"Found existing issue with id: {latest_issue.id}, no updates needed")

        if issue_in_db is not None and issue_schema.published != issue_in_db.published:
            logger.debug(f"Found updates in issue with id: {latest_issue.id}, updating")
            return await self._hot_issues_service.update_issue(self._uow, issue_schema)

        if issue_in_db is None:
            logger.debug(f"Found new issue with id: {latest_issue.id}, adding it")
            return await self._hot_issues_service.add_issue(self._uow, issue_schema)


hot_issues_processor = HotIssuesProcessor(UOWDep)
