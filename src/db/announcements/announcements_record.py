from dataclasses import dataclass
from datetime import datetime


@dataclass
class AnnouncementsRecord:
    id: int
    time: datetime
    channel: int
    message: str
    attachment_url: str

    def __str__(self):
        return f"ID: {self.id}, time: {self.time}, channel: {self.channel}, message: {self.message}, attachment_url: {self.attachment_url}"
