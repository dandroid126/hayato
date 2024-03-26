import asyncio
import threading
from datetime import datetime, timedelta

import pytz
from discord import Client

import src.constants as constants
from src.constants import LOGGER
from src.db.birthday.birthday_dao import BirthdayDao
from src.db.db_manager import DbManager
from src.utils.signal_util import signal_util

TAG = "BirthdayUtil"
BIRTHDAY_TIMEZONE = pytz.timezone('Etc/GMT+12')
BIRTHDAY_REPLACEMENT = "{{BIRTHDAY_REPLACEMENT}}"
BIRTHDAY_MESSAGE_TEMPLATE = f"OHAYAHO!!!!! IT IS {BIRTHDAY_REPLACEMENT}'s BIRTHDAY!!!!! HAPPY BIRTHDAY, {BIRTHDAY_REPLACEMENT}!!!!!"

DATE_FORMAT = '%Y-%m-%d'


class BirthdayUtil:
    def __init__(self, client: Client, channel_id: int):
        self.is_running = False
        self.client = client
        self.channel = client.get_channel(channel_id)
        self.start()

    def start(self):
        self.is_running = True
        loop = asyncio.get_running_loop()
        thread = threading.Thread(target=self._loop, args=(loop, ))
        thread.start()

    def stop(self):
        self.is_running = False

    def _get_birthday_message(self, user_id: int) -> str:
        return BIRTHDAY_MESSAGE_TEMPLATE.replace(BIRTHDAY_REPLACEMENT, self.client.get_user(user_id).mention)

    @staticmethod
    def _get_sleep_delay() -> int:
        now = datetime.now().astimezone(BIRTHDAY_TIMEZONE)
        # Set time as 2 seconds after midnight to prevent rounding error from making it 23:59:59, because then the birthday will be announced repeatedly. 
        tomorrow = datetime.today().astimezone(BIRTHDAY_TIMEZONE).replace(hour=0, minute=0, second=2, microsecond=0) + timedelta(days=1)
        seconds_until_tomorrow = int((tomorrow - now).total_seconds())
        LOGGER.d(TAG, f"seconds_until_tomorrow: {seconds_until_tomorrow}")
        return seconds_until_tomorrow

    def _loop(self, loop):
        # Need to get the DB manager and dao here because it needs to be initialized in the same thread it is used from
        db_manager = DbManager(constants.DB_PATH)
        birthday_dao = BirthdayDao(db_manager)
        while not signal_util.is_interrupted and self.is_running:
            LOGGER.d(TAG, "BirthdayUtil is processing birthdays...")
            birthdays = birthday_dao.get_all_birthdays()
            if birthdays is None:
                LOGGER.d(TAG, "No birthdays to process")
                signal_util.wait(self._get_sleep_delay())
                continue
            for birthday in birthdays:
                LOGGER.d(TAG, f"birthday: {birthday}")
                if birthday.date.strftime(DATE_FORMAT) == datetime.now().astimezone(BIRTHDAY_TIMEZONE).strftime(DATE_FORMAT):
                    # TODO: add try/catch
                    if self.channel is not None:
                        asyncio.run_coroutine_threadsafe(self.channel.send(self._get_birthday_message(birthday.user_id)), loop).result()
                        birthday_dao.update_last_wished_year(birthday.user_id, datetime.now().astimezone(BIRTHDAY_TIMEZONE).year)
            signal_util.wait(self._get_sleep_delay())
        LOGGER.i(TAG, "BirthdaysUtil stopped")
        # TODO: This is some serious spaghetti code. It solves the problem of not being able to close the bot on an interrupt because signal_util captures it instead of it going to the bot,
        #  But this really should not be done this way. There needs to be a way to have multiple threads listening for the interrupt signal to shut down gracefully.
        asyncio.run_coroutine_threadsafe(self.client.close(), loop)
