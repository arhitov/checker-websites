from pydantic import BaseModel
from http import HTTPStatus


class RobotsDTO(BaseModel):
    url: str
    exist: bool
    status: HTTPStatus | None = None
    hash: str | None = None
    content: str | None = None

    def get_sitemap_url(self) -> str | None:
        for line in self.content.splitlines():
            if line.lower().startswith('sitemap:'):
                return line.split(':', 1)[1].strip()
        return None
