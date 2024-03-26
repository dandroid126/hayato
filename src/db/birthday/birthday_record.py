from dataclasses import dataclass
from datetime import datetime


@dataclass
class BirthdayRecord:
    user_id: int
    date: datetime
    last_wished_year: int = 0

    def __str__(self):
        return f" user_id: {self.user_id}, date: {self.date}, last_wished_year: {self.last_wished_year}"
