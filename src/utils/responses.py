import random
from typing import Optional
import re

TAG = "responses.py"

_boy_names = ["otoya", "masato", "tokiya", "syo", "ren", "natsuki", "cecil", "reiji", "ranmaru", "ai", "camus", "eiji", "yamamoto", "van", "eichi", "shion", "nagi", "kira"]

_keyword_lists = [
    [re.compile(fr"i love ({'|'.join(_boy_names)})", re.IGNORECASE)],
    ["ohayaho"],
    [re.compile(r"(?<!\d)69(?!\d)"), re.compile(r"^nice\.$", re.IGNORECASE)],
    ["are you ready?"],
    ["download link", "hand cam", "record stream", "stream recording", "for free"]]

_i_love_responses = ["loves you, too!"]
_ohayoho_responses = ["OHAYAHO!!!!!"]
_sixty_nine_responses = ["nice."]
_are_you_ready_responses = ["10! ARE YOU READY?"]
_piracy_responses = ["OHAYAHO! Please support the series by legal means!"]

response_list = [_i_love_responses, _ohayoho_responses, _sixty_nine_responses, _are_you_ready_responses, _piracy_responses]


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

    for index, keyword_list in enumerate(_keyword_lists):
        for keyword in keyword_list:
            if isinstance(keyword, str):
                if keyword in message.lower():
                    return random.choice(response_list[index])
            elif type(keyword) is re.Pattern:
                match = keyword.search(message.lower())
                if not match:
                    continue
                # TODO: this is kind of lazy. Figure out a better way to do this, because if more than one keyword uses groups, it will not work
                if hasattr(match, "groups") and len(match.groups()) > 0:
                    return f"{match.group(1).capitalize()} {random.choice(response_list[index])}"
                else:
                    return random.choice(response_list[index])
    return None
