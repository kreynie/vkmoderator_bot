from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, validator

from src.utils.html_parser import convert_html_to_text


class Translation(BaseModel):
    lang: str
    title: str
    text: str

    @validator("text")
    def remove_html_stuff(cls, text: str) -> str:
        return convert_html_to_text(text)


class Translations(BaseModel):
    data: list[Translation]
    meta: dict


class Datum(BaseModel):
    id: int
    expired: str | None
    published: str
    status: str
    system_tags: list[str]
    translations: Translations

    @validator("published", pre=True)
    def prepare_published(cls, value: str) -> str:
        """Prepares published date for use with"""
        original_date_time = datetime.fromisoformat(value)
        new_timezone = timezone(timedelta(hours=3))  # +3 GMT
        return original_date_time.astimezone(new_timezone).isoformat()


class Meta(BaseModel):
    total: int
    count: int
    offset: int


class HotIssuesResponseModel(BaseModel):
    meta: Meta
    data: list[Datum]


class HotIssueSchema(BaseModel):
    id: int
    title: str
    text: str
    published: str

    class Config:
        orm_mode = True
