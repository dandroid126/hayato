import json
from datetime import datetime
from typing import Optional

from dateutil import parser

from src.constants import LOGGER
from src.db.announcements.announcements_record import AnnouncementsRecord
from src.db.db_manager import DbManager, db_manager

# Keeping these here for reference, but don't use them because formatted strings in queries are bad.
# TABLE_ANNOUNCEMENTS = 'announcements'
# COLUMN_ID = 'id'
# COLUMN_TIME = 'time'
# COLUMN_CHANNEL = 'channel'
# COLUMN_MESSAGE = 'message'
# COLUMN_ATTACHMENT = 'attachment'

TAG = "AnnouncementsDao"


class AnnouncementsDao:
    def __init__(self, db_manager: DbManager):
        self.db_manager = db_manager

    def get_announcement_by_id(self, row_id: int) -> Optional[AnnouncementsRecord]:
        query = "SELECT * FROM announcements WHERE id=?"
        params = (row_id,)
        LOGGER.i(TAG, f"get_announcement_by_id(): executing {query} with params {params}")
        val = self.db_manager.cursor.execute(query, params).fetchone()
        if val is not None:
            return AnnouncementsRecord(val[0], parser.parse(val[1]), val[2], val[3], json.loads(val[4]))
        return None

    def get_all_announcements(self) -> list[AnnouncementsRecord]:
        query = "SELECT * FROM announcements"
        LOGGER.i(TAG, f"get_all_announcements(): executing {query}")
        vals = self.db_manager.cursor.execute(query).fetchall()
        out = []
        for val in vals:
            out.append(AnnouncementsRecord(val[0], parser.parse(val[1]), val[2], val[3], json.loads(val[4])))
        return out

    def schedule_announcement(self, time: datetime, channel: int, message: str, attachment: dict) -> Optional[AnnouncementsRecord]:
        query = "INSERT INTO announcements(time, channel, message, attachment) VALUES(?, ?, ?, ?) RETURNING *"
        params = (time, channel, message, json.dumps(attachment))
        LOGGER.i(TAG, f"schedule_announcement(): executing {query} with params {params}")
        val = self.db_manager.cursor.execute(query, params).fetchone()
        self.db_manager.connection.commit()
        if val is not None:
            return AnnouncementsRecord(val[0], parser.parse(val[1]), val[2], val[3], json.loads(val[4]))
        return None

    def delete_announcement_by_id(self, row_id: int):
        query = "DELETE FROM announcements WHERE id=? returning *"
        params = (row_id,)
        LOGGER.i(TAG, f"delete_announcement_by_id(): executing {query} with params {params}")
        val = self.db_manager.cursor.execute(query, params).fetchone()
        self.db_manager.connection.commit()
        if val is not None:
            return AnnouncementsRecord(val[0], parser.parse(val[1]), val[2], val[3], json.loads(val[4]))
        return None


announcements_dao = AnnouncementsDao(db_manager)
