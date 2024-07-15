from typing import Optional

from src.constants import LOGGER
from src.db.db_manager import DbManager, db_manager
from src.db.tweet.tweet_record import TweetRecord

# Keeping these here for reference, but don't use them because formatted strings in queries are bad.
# TABLE_TWEETS = 'tweets'
# COLUMN_id = 'tweet_id'
# COLUMN_profile = 'profile'

TAG = "TweetDao"


class TweetDao:
    def __init__(self, db_manager: DbManager):
        self.db_manager = db_manager

    def insert_tweet(self, tweet_record: TweetRecord) -> Optional[TweetRecord]:
        query = "INSERT OR REPLACE INTO tweets(tweet_id, profile) VALUES(?, ?) RETURNING *"
        params = (tweet_record.tweet_id, tweet_record.profile)
        LOGGER.i(TAG, f"insert_tweet(): executing {query} with params {params}")
        val = self.db_manager.cursor.execute(query, params).fetchone()
        self.db_manager.connection.commit()
        if val is not None:
            return TweetRecord(val[0], val[1])
        return None

    def get_tweet_by_id(self, tweet_id: int) -> Optional[TweetRecord]:
        query = "SELECT * FROM tweets WHERE tweet_id=?"
        params = (tweet_id,)
        LOGGER.i(TAG, f"get_tweet_by_id(): executing {query} with params {params}")
        val = self.db_manager.cursor.execute(query, params).fetchone()
        if val is not None:
            return TweetRecord(val[0], val[1])
        return None


tweet_dao = TweetDao(db_manager)
