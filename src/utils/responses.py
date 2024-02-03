import random
from typing import Optional
import re

import src.logger as logger

TAG = "responses.py"

_boy_names = ["otoya", "masato", "tokiya", "syo", "ren", "natsuki", "cecil", "reiji", "ranmaru", "ai", "camus", "eiji", "yamamoto", "van", "eichi", "shion", "nagi", "kira"]

i_love = "i love"
i_love_regex = re.compile(".*" + i_love + r" (\w+).*", re.IGNORECASE)

_keyword_lists = [[i_love], ["ohayaho"], ["69"], ["are you ready?"], ["download link", "hand cam", "record stream", "stream recording", "for free"]]

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

    # Iterate through each keyword list
    for index, keyword_list in enumerate(_keyword_lists):
        # Check if any keyword in the list is in the lowercase message
        match = next((keyword for keyword in keyword_list if keyword in message.lower()), False)
        # If no match, continue to the next keyword list
        if not match:
            continue
        # If the match is "i_love"
        if match == i_love:
            # Try to match the message with the "i_love" regex
            regex_matches = i_love_regex.match(message)
            # If there is a regex match
            if regex_matches:
                try:
                    # Get the index of the matched boy name in the list
                    index = _boy_names.index(regex_matches.group(1).lower())
                    # Return a response with the capitalized boy name and a random "i_love" response
                    return f"{_boy_names[index].capitalize()} {random.choice(_i_love_responses)}"
                except ValueError:
                    # Log an error if the boy name is not found
                    logger.d(TAG, f"get_response(): boy name not found: {regex_matches.group(0)}")
                    return None
        else:
            # Return a random response from the response list corresponding to the matched keyword list index
            return random.choice(response_list[index])
    return None
