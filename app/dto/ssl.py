import re
from datetime import datetime, timedelta, timezone
from app.dto.domain import DomainDTO


class SSLDTO(DomainDTO):
    """
    Данные сертификата.

    Атрибуты:
        domain (str): Унаследовано. Имя домена.
        names (tuple[str, ...]): Список поддерживаемых доменов.
        organization (str | None): Имя организации выдавшая сертификат.
        start_date (datetime): Дата начала действия сертификата.
        end_date (datetime): Дата конец действия сертификата.
    """
    names: tuple[str, ...]
    organization: str | None
    start_date: datetime
    end_date: datetime

    @property
    def is_valid(self) -> bool:
        """Валидны ли сертификат"""
        current_time = datetime.now(timezone.utc)
        return self.is_valid_domain and self.start_date <= current_time <= self.end_date

    @property
    def is_valid_domain(self) -> bool:
        if self.domain in self.names:
            return True
        else:
            """Проверить, соответствует ли домен сертификату (с учетом wildcard)."""
            for name in self.names:
                if name == self.domain:
                    return True
                elif name.startswith('*.'):
                    # Преобразуем wildcard-домен в регулярное выражение
                    regex = re.escape(name).replace(r"\*", r".*")
                    if re.match(f"^{regex}$", self.domain) is not None:
                        return True
        return False

    @property
    def validity_period(self) -> timedelta:
        """Период действия сертификата"""
        return self.end_date - self.start_date

    @property
    def left_period(self) -> timedelta:
        """Период до конца действия сертификата. Может быть отрицательное"""
        current_time = datetime.now(timezone.utc)
        return self.end_date - current_time
