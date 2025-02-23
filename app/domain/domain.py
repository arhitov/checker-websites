import time
import socket
import ssl
from app.ecxeptions.domain import DomainError, DomainPortError
from app.domain.domain_ssl import DomainSSL
from app.request.robots import Robots
from app.dto.domain import DomainDTO, DomainResolve, DomainPort, DomainPortTimersDTO
from app.dto.ssl import SSLDTO
from app.dto.robots import RobotsDTO
from app.dto.sitemap import SitemapDTO
from app.request.sitemap import Sitemap


class Domain:
    def __init__(self, domain: str):
        self.__domain = domain
        self.__timeout = 5
        self.__port_ssl_is_open = None
        self.__robots_dto = None
        self.__sitemap_dto = None

    @property
    def domain(self) -> DomainDTO:
        return DomainDTO(domain=self.__domain)

    def resolve(self) -> DomainResolve:
        """
        Разрешение домена
        :return: IP адрес, Время резолва
        """
        start_time = time.time()
        try:
            ip_address = socket.gethostbyname(self.__domain)
            resolve_time = time.time() - start_time
            return DomainResolve(domain=self.__domain, ip_v4=ip_address, resolve_time=resolve_time)
        except socket.error as e:
            raise DomainError(f"Ошибка при разрешении домена: {e}", self.__domain, e) from e

    def port(self, port: int) -> DomainPort:
        start_time = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.__timeout)
            if port == 443:
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=self.__domain)
            result = sock.connect_ex((self.__domain, port))
            connect_time = time.time() - start_time
            sock.close()
            port_is_open = result == 0
            # Элемент оптимизации
            if port == 443:
                self.__port_ssl_is_open = port_is_open

            return DomainPort(
                domain=self.__domain,
                number=port,
                is_open=port_is_open,
                timers=DomainPortTimersDTO(
                    connect=connect_time,
                ),
            )
        except Exception as e:
            raise DomainPortError(f"Ошибка при проверке порта {port}: {e}", self.__domain, port, e) from e

    def port_ssl_is_open(self) -> bool:
        if self.__port_ssl_is_open is None:
            self.__port_ssl_is_open = self.port(443).is_open
        return self.__port_ssl_is_open

    def ssl(self) -> SSLDTO:
        """Данные сертификата"""
        port_is_open = self.port_ssl_is_open()
        if not port_is_open:
            raise DomainError('Порт 443 не открыт', self.__domain)
        try:
            return DomainSSL(domain=self.__domain).info()
        except Exception as e:
            raise DomainError(f"Ошибка при проверке SSL-сертификата: {e}", self.__domain, e) from e

    def robots(self) -> RobotsDTO:
        if self.__robots_dto is None:
            robots_cls = Robots(self.__domain, 443 if self.port_ssl_is_open() else 80)
            self.__robots_dto = RobotsDTO(
                url=robots_cls.url,
                exist=robots_cls.exist(),
                status=robots_cls.get_status(),
                hash=robots_cls.get_hash() if robots_cls.exist() else None,
                content=robots_cls.get_content() if robots_cls.exist() else None,
            )

        return self.__robots_dto

    def sitemap(self) -> SitemapDTO | None:
        if self.__sitemap_dto is None:
            robots = self.robots()
            if not robots.exist:
                return None
                # raise RobotsError('Файл robots.txt не существует', robots.url)
            sitemap_url = robots.get_sitemap_url()
            if sitemap_url is None:
                return None
                # raise RobotsError('Файл robots.txt не содержит ссылку на sitemap', robots.url)

            sitemap_cls = Sitemap(sitemap_url)
            self.__sitemap_dto = SitemapDTO(
                url=sitemap_cls.url,
                exist=sitemap_cls.exist(),
                status=sitemap_cls.get_status(),
                hash=sitemap_cls.get_hash() if sitemap_cls.exist() else None,
                content=sitemap_cls.get_content() if sitemap_cls.exist() else None,
            )

        return self.__sitemap_dto
