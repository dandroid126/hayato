from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AnnouncementsRecord:
    id: int
    time: datetime
    channel: int
    message: str
    attachment: Optional[dict[str, str | int | bool]] = None

    def __str__(self):
        return f"ID: {self.id}, time: {self.time}, channel: {self.channel}, message: {self.message}, attachment: {self.attachment.get('url') if self.attachment else None}"
