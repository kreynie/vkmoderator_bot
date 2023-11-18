from pydantic import BaseModel, validator


class BaseUserSchema(BaseModel):
    id: int
    first_name: str
    last_name: str


class UserSchema(BaseUserSchema):
    full_name: str | None = None
    screen_name: str | None = None

    @validator("full_name", always=True)
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
    # stuff: list[Stuff] | None  # TODO: доделать

    class Config:
        orm_mode = True
