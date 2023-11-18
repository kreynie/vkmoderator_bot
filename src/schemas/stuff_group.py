from pydantic import BaseModel


class StuffGroup(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
