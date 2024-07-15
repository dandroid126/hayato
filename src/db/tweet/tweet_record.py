from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.utils import common_utils


@dataclass
class TweetRecord:
    tweet_id: int
    profile: str

    @staticmethod
    def get_tweet_record_from_link(link: str) -> Optional[TweetRecord]:
        """
        Parse the link and create a TweetRecord

        Args:
            link (str): The link to parse
        Returns:
            TweetRecord: The parsed TweetRecord
        """

        parts = link.split("/")
        tweet_id = common_utils.cast_to_int(parts[-1]) if len(parts) > 4 else -1
        profile = parts[-3] if len(parts) > 4 else ""

        if tweet_id == -1 or profile == "":
            return None
        return TweetRecord(tweet_id, profile)

    def get_link(self):
        """
        Get the link to the tweet

        Returns:
            str: The link to the tweet
        """
        return f"https://x.com/{self.profile}/status/{self.tweet_id}"

    def get_vxtwitter_link(self):
        """
        Get the link to the tweet as a vxtwitter link

        Returns:
            str: The link to the tweet as a vxtwitter link
        """
        return f"https://vxtwitter.com/{self.profile}/status/{self.tweet_id}"

    def __eq__(self, other):
        if isinstance(other, TweetRecord):
            return self.profile == other.profile and self.tweet_id == other.tweet_id
        elif isinstance(other, int):
            return self.tweet_id == other
        return False
