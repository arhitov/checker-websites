import time
import requests
from http import HTTPStatus
from app.dto.request import MethodDTO, RequestDTO, TimersDTO
from app.request.method import Method
from app.ecxeptions.request import RequestError


def status_is_allowed(status: HTTPStatus) -> bool:
    return status.is_success or status.is_redirection


class Request:
    def __init__(self, domain: str):
        self.__domain = domain
        self.__timeout = 5

    def http_method(self, method: Method, port: int = 80) -> MethodDTO:
        url = f"http{'s' if port == 443 else ''}://{self.__domain}"
        try:
            response = requests.request(method.value, url, timeout=self.__timeout)
            status = HTTPStatus(response.status_code)
            return MethodDTO(
                method=method,
                port=port,
                allowed=status_is_allowed(status),
            )
        except requests.RequestException as e:
            raise RequestError(f"Ошибка при выполнении {method} запроса: {e}", url, e) from e


    def http_method_info(self, method: Method, port: int = 80) -> RequestDTO:
        url = f"http{'s' if port == 443 else ''}://{self.__domain}"
        start_time = time.time()
        try:
            response = requests.request(method.value, url, timeout=self.__timeout)
            content_time = time.time() - start_time
            status = HTTPStatus(response.status_code)
            return RequestDTO(
                domain=self.__domain,
                method=method,
                port=port,
                allowed=status_is_allowed(status),
                content_time=content_time,
                status=status,
                headers=response.headers,
                timers=TimersDTO(content=content_time),
            )
        except requests.RequestException as e:
            raise RequestError(f"Ошибка при выполнении {method} запроса: {e}", url, e) from e
