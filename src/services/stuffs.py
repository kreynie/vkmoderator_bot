from src.database import exceptions as db_exc
from src.schemas import stuff as schemas
from src.utils.enums import StuffGroups
from src.utils.unitofwork import IUnitOfWork


class StuffsService:
    async def add_stuff(
            self,
            uow: IUnitOfWork,
            stuff_in: schemas.StuffCompleteCreateSchema,
    ) -> schemas.Stuff:
        async with uow:
            try:
                await uow.users.add_one(stuff_in.user_create_info.dict())
            except db_exc.EntityAlreadyExists:
                pass

            stuff = await uow.stuffs.add_one(stuff_in.stuff_create_info.dict())
            await uow.commit()
            return stuff

    async def get_stuff_by(self, uow: IUnitOfWork, **filter_by) -> schemas.Stuff:
        async with uow:
            return await uow.stuffs.find_one(**filter_by)

    async def get_stuffs(self, uow: IUnitOfWork, **filter_by) -> list[schemas.Stuff]:
        async with uow:
            return await uow.stuffs.find_all(**filter_by)

    async def get_stuffs_by_group(self, uow: IUnitOfWork, stuff_group: StuffGroups) -> list[schemas.Stuff]:
        async with uow:
            return await self.get_stuffs(uow, group_id=stuff_group.value)

    async def update_stuff(
            self,
            uow: IUnitOfWork,
            stuff_update: schemas.StuffUpdateSchema | schemas.StuffUpdatePartialSchema,
            partial: bool = False,
    ) -> schemas.Stuff:
        async with uow:
            stuff_dict = stuff_update.dict(exclude_unset=partial)
            stuff_id = stuff_dict.pop("id")

            stuff = await uow.stuffs.update_one(data=stuff_dict, id=stuff_id)
            await uow.commit()
            return stuff

    async def delete_stuff(self, uow: IUnitOfWork, stuff_delete: schemas.StuffDeleteSchema) -> None:
        async with uow:
            await uow.stuffs.delete_one(**stuff_delete.dict(exclude_unset=True))
            await uow.commit()
