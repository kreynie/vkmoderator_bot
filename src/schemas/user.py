from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator


class BaseUserSchema(BaseModel):
    id: int
    first_name: str
    last_name: str


class UserSchema(BaseUserSchema):
    full_name: str | None = None
    screen_name: str | None = None

    @model_validator(mode="after")
    def set_full_name(self) -> Self:
        self.full_name = f"{self.first_name} {self.last_name}"
        return self


class UserCreateSchema(BaseUserSchema):
    pass


class UserUpdateSchema(UserCreateSchema):
    pass


class UserUpdatePartialSchema(BaseUserSchema):
    first_name: str | None
    last_name: str | None


class User(UserSchema):
    model_config = ConfigDict(from_attributes=True)
