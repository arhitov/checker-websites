from pydantic import BaseModel
from http import HTTPStatus
from app.dto.domain import DomainDTO
from app.request.method import Method


class MethodDTO(BaseModel):
    method: Method
    port: int
    allowed: bool


class TimersDTO(BaseModel):
    content: float


class RequestDTO(DomainDTO):
    method: Method
    query: str = ''
    status: HTTPStatus
    headers: dict = {}
    timers: TimersDTO
