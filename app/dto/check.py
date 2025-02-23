from pydantic import BaseModel
from app.dto.domain import DomainDTO, DomainResolve, DomainPort
from app.dto.ssl import SSLDTO
from app.dto.request import MethodDTO
from app.dto.robots import RobotsDTO
from app.dto.sitemap import SitemapDTO


class CheckDTO(BaseModel):
    domain: DomainDTO
    resolve: DomainResolve | None = None
    ssl: SSLDTO | None = None
    ports: tuple[DomainPort, ...] = tuple()
    ports_methods: dict[int, tuple[MethodDTO, ...]] = tuple()
    robots: RobotsDTO
    sitemap: SitemapDTO | None

    def get_port(self, port: int) -> DomainPort | None:
        for port_dto in self.ports:
            if port_dto.number == port:
                return port_dto
        return None

    def has_port_methods(self, port: int) -> bool:
        return port in self.ports_methods

    def get_port_methods(self, port: int) -> tuple[MethodDTO, ...]:
        return self.ports_methods[port] if self.has_port_methods(port) else tuple()

    def is_ssl(self) -> bool:
        return self.ssl is not None

