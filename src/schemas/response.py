from typing import Any

from pydantic import BaseModel


class RequestResponse(BaseModel):
    status_code: int
    content: Any
