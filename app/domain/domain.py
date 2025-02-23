import time
import socket
import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from app.ecxeptions.domain import DomainError, DomainPortError
from app.dto.domain import DomainDTO, DomainResolve, DomainPort, DomainPortTimersDTO
from app.dto.ssl import SSLDTO


class Domain:
    def __init__(self, domain: str):
        self.__domain = domain
        self.__port_ssl_is_open = None
        self.__timeout = 5

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

    def ssl(self) -> SSLDTO:
        """
        :return: Валидны ли сертификат, дата начала действия сертификата, дата конец действия сертификата
        """
        port_is_open = self.__port_ssl_is_open if self.__port_ssl_is_open is not None else self.port(443)[0]
        if not port_is_open:
            raise DomainError('Порт 443 не открыт', self.__domain)
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.__domain, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=self.__domain) as source_sock:
                    cert_der = source_sock.getpeercert(binary_form=True)
                    cert = x509.load_der_x509_certificate(cert_der, default_backend())

                    # Проверка срока действия сертификата
                    start_date = cert.not_valid_before_utc
                    end_date = cert.not_valid_after_utc

                    return SSLDTO(
                        domain=self.__domain,
                        start_date=start_date,
                        end_date=end_date,
                    )
        except Exception as e:
            raise DomainError(f"Ошибка при проверке SSL-сертификата: {e}", self.__domain, e) from e
