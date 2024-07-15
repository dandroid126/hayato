from __future__ import annotations

import asyncio
import threading
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final

import numpy
from discord import Client
from playwright.async_api import async_playwright

import src.constants as constants
from src.constants import LOGGER
from src.db.db_manager import DbManager
from src.db.tweet.tweet_dao import TweetDao
from src.db.tweet.tweet_record import TweetRecord
from src.utils.signal_util import signal_util

TAG = "TwitterUtil"

SLEEP_TIME_BASE: Final[int] = 60
WAIT_TIME: Final[int] = 5000
RESPONSE: Final[str] = "response"


DATA: Final[str] = "data"
USER: Final[str] = "user"
RESULT: Final[str] = "result"
TIMELINE_V2: Final[str] = "timeline_v2"
TIMELINE: Final[str] = "timeline"
INSTRUCTIONS: Final[str] = "instructions"
TYPE: Final[str] = "type"
TIMELINE_ADD_ENTRIES: Final[str] = "TimelineAddEntries"
ENTRIES: Final[str] = "entries"
ENTRY_ID: Final[str] = "entryId"
TWEET_ID_PREFIX: Final[str] = "tweet-"
USER_TWEETS: Final[str] = "UserTweets"
VIEWPORT: Final[dict[str, int]] = MappingProxyType({"width": 1920, "height": 1080})
XHR: Final[str] = "xhr"

PROFILE_NAME_REPLACEMENT: Final[str] = "{{PROFILE_NAME}}"
TWEET_ID_REPLACEMENT: Final[str] = "{{TWEET_ID}}"
TWEET_URL_PATTERN: Final[str] = f"https://x.com/{PROFILE_NAME_REPLACEMENT}/status/{TWEET_ID_REPLACEMENT}"
TWITTER_PROFILE_URL_PATTERN: Final[str] = f"https://x.com/{PROFILE_NAME_REPLACEMENT}"


class TwitterUtil:

    def __init__(self, client: Client, tweets_configs: list[TweetsConfig]):
        self.is_running = False
        self.client = client
        self.tweets_configs = tweets_configs
        self.config_index = 0
        self.rng = numpy.random.default_rng()
        self.start()

    def start(self):
        """
        Start the loop
        """
        self.is_running = True
        loop = asyncio.get_running_loop()
        thread = threading.Thread(target=self._loop, args=(loop,))
        thread.start()

    def stop(self):
        """
        Gracefully stop the loop the next time it completes
        """
        LOGGER.d(TAG, "stop")
        self.is_running = False

    def get_sleep_time(self) -> int:
        """
        Get the time to sleep before refreshes in seconds.

        Notes:
            The sleep time is a normal distribution with mean SLEEP_TIME_BASE and standard deviation SLEEP_TIME_BASE / 10
            The purpose of this is to avoid being detected as a bot by twitter

        Returns:
            int: Sleep time in seconds
        """
        sleep_time = int(self.rng.normal(SLEEP_TIME_BASE, SLEEP_TIME_BASE / 10))
        LOGGER.d(TAG, f"get_sleep_time: sleep_time: {sleep_time}")
        return sleep_time

        # return SLEEP_TIME_BASE

    def _loop(self, loop: asyncio.AbstractEventLoop):
        """
        The loop to run
        """

        db_manager = DbManager(constants.DB_PATH)
        tweets_dao = TweetDao(db_manager)
        while not signal_util.is_interrupted and self.is_running:
            tweets_config = self.tweets_configs[self.config_index]
            profile = tweets_config.profile
            channel = self.client.get_channel(tweets_config.channel_id)
            tweets = asyncio.run_coroutine_threadsafe(TwitterUtil.get_tweets_from_profile(profile), loop).result()
            for tweet in tweets:
                tweet_record: TweetRecord = TweetRecord.get_tweet_record_from_link(tweet)
                if tweet_record and not tweets_dao.get_tweet_by_id(tweet_record.tweet_id):
                    asyncio.run_coroutine_threadsafe(channel.send(tweet_record.get_vxtwitter_link()), loop).result()
                    tweets_dao.insert_tweet(tweet_record)
            self.config_index = (self.config_index + 1) % len(self.tweets_configs)
            signal_util.wait(self.get_sleep_time())

    @staticmethod
    async def get_tweets_from_profile(profile_name: str) -> list[str]:
        """
        get tweets from profile

        modified from https://scrapfly.io/blog/how-to-scrape-twitter/

        Args:
            profile_name (str): name of the profile
        Returns:
            list: list of tweets from profile as vxtwitter links
        """
        _xhr_calls = []

        def intercept_response(response):
            """capture all background requests and save them"""
            # we can extract details from background requests
            if response.request.resource_type == XHR:
                _xhr_calls.append(response)
            return response

        tweets = []
        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch()
                context = await browser.new_context(viewport=VIEWPORT.copy())
                page = await context.new_page()

                # enable background request intercepting:
                page.on(RESPONSE, intercept_response)
                # go to url and wait for the page to load
                await page.goto(TWITTER_PROFILE_URL_PATTERN.replace(PROFILE_NAME_REPLACEMENT, profile_name))
                await page.wait_for_timeout(WAIT_TIME)

                # find all tweet background requests:
                tweet_calls = [f for f in _xhr_calls if USER_TWEETS in f.url]
                for xhr in tweet_calls:
                    data = await xhr.json()
                    for instruction in data[DATA][USER][RESULT][TIMELINE_V2][TIMELINE][INSTRUCTIONS]:
                        if instruction[TYPE] == TIMELINE_ADD_ENTRIES:
                            for entry in instruction[ENTRIES]:
                                if entry[ENTRY_ID].startswith(TWEET_ID_PREFIX):
                                    tweet_id = entry[ENTRY_ID].split('-')[1]
                                    tweet_url = TWEET_URL_PATTERN.replace(PROFILE_NAME_REPLACEMENT, profile_name).replace(TWEET_ID_REPLACEMENT, tweet_id)
                                    tweets.append(tweet_url)
        except TimeoutError as e:
            LOGGER.e(TAG, f"get_tweets_from_profile: TimeoutError", e)
        finally:
            if browser:
                await browser.close()
        return tweets


@dataclass
class TweetsConfig:
    profile: str
    channel_id: int
