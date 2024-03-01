import csv
import os
import random
import re
from typing import Optional

from dotenv import load_dotenv

from src.constants import LOGGER

TAG = "responses.py"

load_dotenv()
RESPONSES_FILE_PATH = os.getenv('RESPONSES_FILE_PATH')

_keyword_lists = []
_response_lists = []
_last_known_good_file = None


def load_responses_file():
    global _keyword_lists, _response_lists, _last_known_good_file

    keyword_lists_old = _keyword_lists.copy()
    response_lists_old = _response_lists.copy()

    _keyword_lists = []
    _response_lists = []

    try:
        with open(RESPONSES_FILE_PATH, "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                _keyword_lists.append([parse_keyword(keyword) for keyword in row[0].split(";;")])
                _response_lists.append([parse_response(response) for response in row[1].split(";;")])
            csv_file.seek(0)
            _last_known_good_file = csv_file.read().replace("\\", "\\\\\\")
        LOGGER.i(TAG, "Successfully loaded responses file.")
        LOGGER.d(TAG, str(_keyword_lists))
        LOGGER.d(TAG, str(_response_lists))
        return True
    except Exception as e:
        LOGGER.e(TAG, f"Error loading responses file: {e}")
        _keyword_lists = keyword_lists_old
        _response_lists = response_lists_old
        return False


def parse_keyword(keyword: str) -> str | re.Pattern:
    keyword = keyword.strip().lower()
    if keyword == "":
        raise ValueError("Keyword cannot be empty.")
    if keyword.startswith('r"'):
        if keyword.endswith('/i"'):
            keyword = re.compile(fr"{keyword[2:-3]}", re.IGNORECASE)
        else:
            keyword = re.compile(fr"{keyword[2:-1]}")
    return keyword


def parse_response(response: str) -> str:
    response = response.strip()
    if response == "":
        raise ValueError("Response cannot be empty.")
    if response.startswith('\\'):
        response = response[1:]
    return response


def get_all_responses():
    return f"keywords: {_keyword_lists}\nresponses: {_response_lists}"


def get_responses_file():
    return _last_known_good_file


def get_response(message: str) -> Optional[str]:
    """
    Get a response based on the input message.

    Args:
    message (str): The input message to match against keyword lists.

    Returns:
    Optional[str]: The response based on the input message, or None if no match is found.
    """
    if message is None:
        return None

    global _keyword_lists, _response_lists
    for index, keyword_list in enumerate(_keyword_lists):
        for keyword in keyword_list:
            if isinstance(keyword, str) and keyword in message.lower():
                return random.choice(_response_lists[index])
            elif isinstance(keyword, re.Pattern) and keyword.search(message.lower()):
                return random.choice(_response_lists[index])
    return None


load_responses_file()
