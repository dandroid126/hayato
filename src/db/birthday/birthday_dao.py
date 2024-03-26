from datetime import datetime
from typing import Optional

from dateutil import parser

from src.constants import LOGGER
from src.db.birthday.birthday_record import BirthdayRecord
from src.db.db_manager import DbManager, db_manager

# Keeping these here for reference, but don't use them because formatted strings in queries are bad.
# TABLE_BIRTHDAY = 'birthdays'
# COLUMN_user_id = 'user_id'
# COLUMN_DATE = 'date'

TAG = "BirthdayDao"


class BirthdayDao:
    def __init__(self, db_manager: DbManager):
        self.db_manager = db_manager

    def get_all_birthdays(self) -> list[BirthdayRecord]:
        query = "SELECT * FROM birthdays"
        LOGGER.i(TAG, f"get_all_birthdays(): executing {query}")
        vals = self.db_manager.cursor.execute(query).fetchall()
        out = []
        for val in vals:
            out.append(BirthdayRecord(val[0], parser.parse(val[1]), val[2]))
        return out

    def get_birthday_by_user_id(self, user_id: int) -> Optional[BirthdayRecord]:
        query = "SELECT * FROM birthdays WHERE user_id=?"
        params = (user_id,)
        LOGGER.i(TAG, f"get_birthday_by_user_id(): executing {query} with params {params}")
        val = self.db_manager.cursor.execute(query, params).fetchone()
        if val is not None:
            return BirthdayRecord(val[0], parser.parse(val[1]), val[2])
        return None

    def learn_birthday(self, user_id: int, date: datetime) -> Optional[BirthdayRecord]:
        query = "INSERT OR REPLACE INTO birthdays(user_id, date, last_wished_year) VALUES(?, ?, ?) RETURNING *"
        params = (user_id, date, 0)
        LOGGER.i(TAG, f"remember_birthday(): executing {query} with params {params}")
        val = self.db_manager.cursor.execute(query, params).fetchone()
        self.db_manager.connection.commit()
        if val is not None:
            return BirthdayRecord(val[0], parser.parse(val[1]), val[2])
        return None

    def forget_birthday(self, user_id: int) -> Optional[BirthdayRecord]:
        query = "DELETE FROM birthdays WHERE user_id=? returning *"
        params = (user_id,)
        LOGGER.i(TAG, f"forget_birthday(): executing {query} with params {params}")
        val = self.db_manager.cursor.execute(query, params).fetchone()
        self.db_manager.connection.commit()
        if val is not None:
            return BirthdayRecord(val[0], parser.parse(val[1]), val[2])
        return None

    def update_last_wished_year(self, user_id: int, last_wished_year: int) -> Optional[BirthdayRecord]:
        query = "UPDATE birthdays SET last_wished_year=? WHERE user_id=? returning *"
        params = (last_wished_year, user_id)
        LOGGER.i(TAG, f"update_last_wished_year(): executing {query} with params {params}")
        val = self.db_manager.cursor.execute(query, params).fetchone()
        self.db_manager.connection.commit()
        if val is not None:
            return BirthdayRecord(val[0], parser.parse(val[1]), val[2])
        return None


birthday_dao = BirthdayDao(db_manager)
