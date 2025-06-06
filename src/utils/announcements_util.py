import asyncio
import threading
from datetime import datetime
from typing import Final

import discord
from discord import Client
from tzlocal import get_localzone

from src import constants
from src.constants import LOGGER
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
        self.is_running = True
        loop = asyncio.get_running_loop()
        thread = threading.Thread(target=self._loop, args=(loop, ))
        thread.start()

    def stop(self):
        self.is_running = False

    def _loop(self, loop):
        db_manager = DbManager(constants.DB_PATH)
        announcements_dao = AnnouncementsDao(db_manager)
        while not signal_util.is_interrupted and self.is_running:
            LOGGER.d(TAG, "AnnouncementsUtil is processing announcements...")
            announcements = announcements_dao.get_all_announcements()
            if announcements is None:
                LOGGER.d(TAG, "No announcements to process")
                signal_util.wait(SLEEP_DELAY)
                continue
            for announcement in announcements:
                LOGGER.d(TAG, f"announcement: {announcement}")
                if announcement.time < datetime.now(get_localzone()):
                    channel = self.client.get_channel(announcement.channel)
                    # TODO: add try/catch
                    if channel is not None:
                        attachment_from_announcement = discord.Attachment(data=announcement.attachment, state=self.client._get_state()) if announcement.attachment else None
                        file = asyncio.run_coroutine_threadsafe(attachment_from_announcement.to_file(), loop).result() if attachment_from_announcement else discord.utils.MISSING
                        asyncio.run_coroutine_threadsafe(channel.send(announcement.message, file=file), loop).result()
                        announcements_dao.delete_announcement_by_id(announcement.id)
            signal_util.wait(SLEEP_DELAY)
        self.stop()
        LOGGER.i(TAG, "AnnouncementsUtil stopped")
