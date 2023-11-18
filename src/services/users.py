from src.schemas import user as schemas
from src.utils.unitofwork import IUnitOfWork


class UsersService:
    async def add_user(
            self,
            uow: IUnitOfWork,
            user_in: schemas.UserCreateSchema,
    ) -> schemas.User:
        async with uow:
            user = await uow.users.add_one(user_in.dict())
            await uow.commit()
            return user

    async def get_user_by(self, uow: IUnitOfWork, **filter_by) -> schemas.User | None:
        async with uow:
            return await uow.users.find_one(**filter_by)

    async def get_users(self, uow: IUnitOfWork) -> list[schemas.User]:
        async with uow:
            return await uow.users.find_all()

    async def update_user(
            self,
            uow: IUnitOfWork,
            user_update: schemas.UserUpdateSchema | schemas.UserUpdatePartialSchema,
            partial: bool = False,
    ) -> schemas.User | None:
        async with uow:
            user_dict = user_update.dict(exclude_unset=partial)
            user_id = user_dict.pop("id")

            user = await uow.users.update_one(data=user_dict, id=user_id)
            await uow.commit()
            return user

    async def delete_user(self, uow: IUnitOfWork, user_id: int) -> None:
        async with uow:
            await uow.users.delete_one(id=user_id)
            await uow.commit()
