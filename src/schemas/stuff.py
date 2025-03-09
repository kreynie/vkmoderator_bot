from pydantic import BaseModel, ConfigDict

from .stuff_group import StuffGroup
from .user import User, UserCreateSchema


class StuffBaseSchema(BaseModel):
    user_id: int

    group_id: int
    key: int
    allowance: int


class StuffSchema(StuffBaseSchema):
    id: int


class StuffCreateSchema(StuffBaseSchema):
    pass


class StuffCompleteCreateSchema(BaseModel):
    user_create_info: UserCreateSchema
    stuff_create_info: StuffCreateSchema


class StuffUpdateSchema(StuffSchema):
    pass


class StuffUpdatePartialSchema(StuffSchema):
    user_id: int | None = None
    group_id: int | None = None
    key: int | None = None
    allowance: int | None = None


class StuffDeleteSchema(StuffUpdatePartialSchema):
    pass


class Stuff(StuffSchema):
    user: User
    group: StuffGroup

    model_config = ConfigDict(from_attributes=True)
