from src.schemas.hot_issues import HotIssueSchema, HotIssuesResponseModel
from src.services.hot_issues import HotIssuesService
from src.utils.dependencies import UOWDep
from src.utils.unitofwork import IUnitOfWork
from config import logger


class HotIssuesProcessor:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow
        self._hot_issues_service = HotIssuesService()
        self.is_cache_updated: bool = False
        self._cache: dict[int, HotIssueSchema] | dict = {}
        self._last_hot_issue: HotIssueSchema | None = None

    @property
    def cache(self) -> dict[int, HotIssueSchema]:
        return self._cache

    @cache.setter
    def cache(self, v: dict[int, HotIssueSchema]) -> None:
        self.cache.update(v)
        if v:
            self.is_cache_updated = True
            self.last_hot_issue = tuple(v.values())[0]

    @property
    def last_hot_issue(self) -> HotIssueSchema | None:
        return self._last_hot_issue

    @last_hot_issue.setter
    def last_hot_issue(self, v: HotIssueSchema) -> None:
        self._last_hot_issue = v

    async def initialize_cache(self) -> None:
        logger.info("Initializing cache for HotIssuesProcessor")
        last_issue = await self._hot_issues_service.get_last_issue(self._uow)
        if last_issue is None:
            logger.debug("No issues was found in database, first cache will be empty")
            self._cache = {}
        else:
            logger.debug(f"Adding last issue from database to cache with id: {last_issue.id}")
            self._cache = {last_issue.id: last_issue}

    async def process_issues(self, issues: HotIssuesResponseModel) -> None:
        latest_issue = issues.data[0]
        issue_details = latest_issue.translations.data[0]  # get only first translation version
        issue_schema = HotIssueSchema(
            id=latest_issue.id,
            title=issue_details.title,
            text=issue_details.text,
            published=latest_issue.published,
        )
        if latest_issue.id in self.cache and latest_issue.published != self.cache[latest_issue.id].published:
            logger.debug(f"Found updates in issue with id: {latest_issue.id}, updating")
            updated_issue = await self._hot_issues_service.update_issue(self._uow, issue_schema)
            self.cache = {latest_issue.id: updated_issue}
            return

        if latest_issue.id not in self.cache:
            logger.debug(f"Found new issue with id: {latest_issue.id}, adding it")
            new_issue = await self._hot_issues_service.add_issue(self._uow, issue_schema)
            self.cache = {latest_issue.id: new_issue}
            return
        logger.debug("No new issues were found")


hot_issues_processor = HotIssuesProcessor(UOWDep)
