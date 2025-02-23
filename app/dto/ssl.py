from datetime import datetime, timedelta, timezone
from app.dto.domain import DomainDTO


class SSLDTO(DomainDTO):
    start_date: datetime
    end_date: datetime

    @property
    def is_valid(self) -> bool:
        current_time = datetime.now(timezone.utc)
        return self.start_date <= current_time <= self.end_date

    @property
    def validity_period(self) -> timedelta:
        return self.end_date - self.start_date

    @property
    def left_period(self) -> timedelta:
        current_time = datetime.now(timezone.utc)
        return self.end_date - current_time
