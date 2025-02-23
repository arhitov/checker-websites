import requests
import hashlib
from http import HTTPStatus
from app.ecxeptions.sitemap import SitemapError


class Sitemap:
    def __init__(self, sitemap_url: str):
        self.__url = sitemap_url
        self.__response = None
        self.__status = None
        self.__content = None

    @property
    def url(self) -> str:
        return self.__url

    def exist(self) -> bool:
        try:
            return self.__get_response().status_code == 200
        except SitemapError:
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
                raise SitemapError(
                    f'При загрузки файла код ответа {response.status_code} вместо ожидаемого 200',
                    url=self.__url
                )
        return self.__content

    def __get_response(self):
        if self.__response is None:
            try:
                self.__response = requests.get(self.__url, allow_redirects=False)
            except Exception as e:
                raise SitemapError(
                    'Не удалось получить файл',
                    url=self.__url,
                    original_exception=e
                )
        return self.__response
