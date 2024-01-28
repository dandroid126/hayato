from dataclasses import dataclass
from datetime import datetime


@dataclass
class AnnouncementsRecord:
    id: int
    time: datetime
    channel: int
    message: str

    def __str__(self):
        return f"ID: {self.id}, time:{self.time}, channel: {self.channel}, message: {self.message}"
