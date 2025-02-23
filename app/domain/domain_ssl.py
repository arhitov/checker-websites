import socket
import ssl
import re
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from app.dto.ssl import SSLDTO


class DomainSSL:
    def __init__(self, domain: str):
        self.__domain = domain

    def info(self) -> SSLDTO:

        cert = self.__get_certificate()

        # Срок действия сертификата
        start_date = cert.not_valid_before_utc
        end_date = cert.not_valid_after_utc

        # Проверка Subject Alternative Name (SAN)
        ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        san = ext.value.get_values_for_type(x509.DNSName)

        # Ищем атрибут Organization Name (O)
        organizations = cert.issuer.get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME)
        organization = organizations[0].value if organizations else None

        return SSLDTO(
            domain=self.__domain,
            names=tuple(san),
            organization=organization,
            start_date=start_date,
            end_date=end_date,
        )

        # context = ssl.create_default_context()
        # with socket.create_connection((self.__domain, 443)) as sock:
        #     with context.wrap_socket(sock, server_hostname=self.__domain) as source_sock:
        #         cert_der = source_sock.getpeercert(binary_form=True)
        #         cert = x509.load_der_x509_certificate(cert_der, default_backend())
        #
        #         # Проверка срока действия сертификата
        #         start_date = cert.not_valid_before_utc
        #         end_date = cert.not_valid_after_utc
        #
        #         return SSLDTO(
        #             domain=self.__domain,
        #             start_date=start_date,
        #             end_date=end_date,
        #         )

    def __get_certificate(self, port=443):
        """Получить сертификат с указанного хоста."""
        cert = ssl.get_server_certificate((self.__domain, port))
        return x509.load_pem_x509_certificate(cert.encode(), default_backend())

