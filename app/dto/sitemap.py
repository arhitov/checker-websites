from pydantic import BaseModel
from http import HTTPStatus


class SitemapDTO(BaseModel):
    url: str
    exist: bool
    status: HTTPStatus | None = None
    hash: str | None = None
    content: str | None = None
