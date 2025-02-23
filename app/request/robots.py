import requests
import hashlib
from http import HTTPStatus
from app.ecxeptions.robots import RobotsError


class Robots:
    def __init__(self, domain: str, port: int):
        self.__domain = domain
        self.__port = port
        self.__response = None
        self.__status = None
        base_url = f'http{'s' if port == 443 else ''}://{self.__domain}'
        # Получаем robots.txt
        self.__url = f'{base_url}/robots.txt'
        self.__content = None

    @property
    def url(self) -> str:
        return self.__url

    def exist(self) -> bool:
        try:
            return self.__get_response().status_code == 200
        except RobotsError:
            return False

    def get_status(self) -> HTTPStatus:
        return HTTPStatus(self.__get_response().status_code)

    def get_hash(self) -> str:
        return hashlib.sha256(self.get_content().encode('utf-8')).hexdigest()

    def get_content(self) -> str:
        if self.__content is None:
            response = self.__get_response()
            if response.status_code == 200:
                self.__content = response.text
            else:
                raise RobotsError(
                    f'При загрузки файла код ответа {response.status_code} вместо ожидаемого 200',
                    url=self.__url
                )
        return self.__content

    def __get_response(self):
        if self.__response is None:
            try:
                self.__response = requests.get(self.__url, allow_redirects=False)
            except Exception as e:
                raise RobotsError(
                    'Не удалось получить файл',
                    url=self.__url,
                    original_exception=e
                )
        return self.__response
