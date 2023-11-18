from src.utils.unitofwork import IUnitOfWork
from src.schemas.hot_issues import HotIssueSchema


class HotIssuesService:
    async def add_issue(self, uow: IUnitOfWork, issue_in: HotIssueSchema) -> HotIssueSchema:
        async with uow:
            issue = await uow.hot_issues.add_one(issue_in.dict())
            await uow.commit()
            return issue

    async def get_issue_by(self, uow: IUnitOfWork, **filter_by) -> HotIssueSchema | None:
        async with uow:
            return await uow.hot_issues.find_one(**filter_by)

    async def get_last_issue(self, uow: IUnitOfWork) -> HotIssueSchema | None:
        async with uow:
            return await uow.hot_issues.find_last()

    async def get_issues(self, uow: IUnitOfWork, offset: int = 0, limit: int = 5) -> list[HotIssueSchema]:
        async with uow:
            return await uow.hot_issues.find_all(offset=offset, limit=limit)

    async def update_issue(self, uow: IUnitOfWork, updated_issue: HotIssueSchema) -> HotIssueSchema:
        async with uow:
            issue_id = updated_issue.id
            issue = await uow.hot_issues.update_one(data=updated_issue.dict(exclude={"id"}), id=issue_id)
            await uow.commit()
            return issue

    async def delete_issue(self, uow: IUnitOfWork, issue_id: int) -> None:
        async with uow:
            await uow.hot_issues.delete_one(id=issue_id)
            await uow.commit()
