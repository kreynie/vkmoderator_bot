from pydantic import BaseModel, field_validator


class BaseUserSchema(BaseModel):
    id: int
    first_name: str
    last_name: str


class UserSchema(BaseUserSchema):
    full_name: str | None = None
    screen_name: str | None = None

    @field_validator("full_name")
    @classmethod
    def set_full_name(cls, v, values) -> str:
        return f"{values['first_name']} {values['last_name']}"


class UserCreateSchema(BaseUserSchema):
    pass


class UserUpdateSchema(UserCreateSchema):
    pass


class UserUpdatePartialSchema(BaseUserSchema):
    first_name: str | None
    last_name: str | None


class User(UserSchema):
    class Config:
        orm_mode = True
