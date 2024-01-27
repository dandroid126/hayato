import re
import src.logger as logger

TAG = "input_sanitizer.py"
ALPHANUMERIC = '^[A-Za-z0-9]+$'
ALPHABETICAL = '^[A-Za-z]+$'
NUMERICAL = '^[0-9]+$'
HEXADECIMAL = '^[A-F0-9]+$'


def check_length(text, min_length, max_length):
    logger.d(TAG, f"check_length: input: {text}; max_length: {max_length}; min_length: {min_length}")
    if max_length >= len(text) >= min_length:
        return True
    return False


def check_pattern(text, pattern):
    logger.d(TAG, f"check_pattern: input: {text}; pattern: {pattern}")
    if re.search(pattern, text):
        return True
    return False
