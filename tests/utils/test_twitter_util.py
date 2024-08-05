import unittest
from unittest.mock import MagicMock

from src import constants
# from constants import LOGGER
from src.db.db_manager import DbManager
from src.db.tweet.tweet_dao import TweetDao
from src.utils.twitter_util import TwitterUtil

TAG = "TestTwitterUtil"


class TestTwitterUtil(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # LOGGER.d(TAG, "setUpClass")
        TwitterUtil.start = MagicMock(return_value=None)
        cls.twitter_util = TwitterUtil(None, None)

    def test_something(self):
        db_manager = DbManager(constants.DB_PATH)
        tweets_dao = TweetDao(db_manager)
        got_tweets = tweets_dao.get_all_tweets()

        assert 1811596771682058314 in got_tweets

#     def test_get_sleep_time(self):
#         # expected = 60
#
#         # old_start = TestTwitterUtil.twitter_util.start
#         # TestTwitterUtil.twitter_util.start = MagicMock(return_value=None)
#         sleep_times = []
#         for _ in range(10000):
#             sleep_times.append(TestTwitterUtil.twitter_util.get_sleep_time())
#
#         import matplotlib.pyplot as plt
#         plt.hist(sleep_times, bins=200)
#         plt.show()
#
#
#         # LOGGER.d(TAG, f"sleep_times: {sleep_times}")
#         # expected = int(sum(sleep_times) / len(sleep_times))
#         # actual = TestTwitterUtil.twitter_util.get_sleep_time()
#         # LOGGER.d(TAG, f"actual: {actual}")
#         # LOGGER.d(TAG, f"expected: {expected}, actual: {actual}")
#         # self.assertEqual(expected, actual)
#
#         # TestTwitterUtil.twitter_util.start = old_start
