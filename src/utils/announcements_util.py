import asyncio
import threading
from datetime import datetime
from typing import Final
from tzlocal import get_localzone

from discord import Client

from src import constants, logger
from src.db.announcements.announcements_dao import AnnouncementsDao
from src.db.db_manager import DbManager
from src.utils.signal_util import signal_util

TAG = "AnnouncementsUtil"
SLEEP_DELAY: Final = 60  # One minute


class AnnouncementsUtil:
    def __init__(self, client: Client):
        self.is_running = False
        self.client = client
        self.start()

    def start(self):
        loop = asyncio.get_running_loop()
        thread = threading.Thread(target=self._loop, args=(loop, ))
        thread.start()

    def stop(self):
        self.is_running = False

    def _loop(self, loop):
        self.is_running = True
        db_manager = DbManager(constants.DB_PATH)
        announcements_dao = AnnouncementsDao(db_manager)
        while not signal_util.is_interrupted and self.is_running:
            logger.d(TAG, "AnnouncementsUtil is processing announcements...")
            announcements = announcements_dao.get_all_announcements()
            if announcements is None:
                logger.d(TAG, "No announcements to process")
                signal_util.wait(SLEEP_DELAY)
                continue
            for announcement in announcements:
                logger.d(TAG, f"announcement: {announcement}")
                if announcement.time < datetime.now(get_localzone()):
                    channel = self.client.get_channel(announcement.channel)
                    # TODO: add try/catch
                    if channel is not None:
                        asyncio.run_coroutine_threadsafe(channel.send(announcement.message), loop)
                        announcements_dao.delete_announcement_by_id(announcement.id)
            signal_util.wait(SLEEP_DELAY)
        logger.i(TAG, "AnnouncementsUtil stopped")
        # TODO: This is some serious spaghetti code. It solves the problem of not being able to close the bot on an interrupt because signal_util captures it instead of it going to the bot,
        #  But this really should not be done this way. There needs to be a way to have multiple threads listening for the interrupt signal to shut down gracefully.
        asyncio.run_coroutine_threadsafe(self.client.close(), loop)


