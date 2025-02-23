import re
from pydantic import BaseModel, field_validator


class DomainDTO(BaseModel):
    domain: str


class DomainResolve(DomainDTO):
    ip_v4: str
    resolve_time: float

    # Валидатор для поля ip_v4
    @field_validator('ip_v4')
    def validate_ip_v4(cls, value):
        # Регулярное выражение для проверки IPv4
        ipv4_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        if not ipv4_pattern.match(value):
            raise ValueError('Invalid IPv4 address')
        # Проверка, что каждый октет находится в диапазоне 0-255
        octets = value.split('.')
        for octet in octets:
            if not 0 <= int(octet) <= 255:
                raise ValueError('Invalid IPv4 address: octet out of range')
        return value

    # Виртуальное свойство ip, доступное только для чтения
    @property
    def ip(self) -> str:
        return self.ip_v4


class DomainPortTimersDTO(BaseModel):
    connect: float


class DomainPort(DomainDTO):
    number: int
    is_open: bool
    timers: DomainPortTimersDTO
