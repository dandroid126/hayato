from dataclasses import dataclass
from datetime import datetime


@dataclass
class AnnouncementsRecord:
    id: int
    time: datetime
    channel: int
    message: str
    attachment: dict[str, str | int | bool]

    def __str__(self):
        return f"ID: {self.id}, time: {self.time}, channel: {self.channel}, message: {self.message}, attachment: {self.attachment.get('url')}"
