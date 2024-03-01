import os
from typing import Final
from logger import Logger


import pytz

SCRIPT_PATH: Final = os.path.realpath(__file__)
DIR_PATH: Final = f"{os.path.dirname(SCRIPT_PATH)}/../"
OUT_PATH: Final = f"{DIR_PATH}/out/"
COMMAND_PREFIX: Final = "&"
LOGGER: Final = Logger(OUT_PATH)

DB_PATH: Final = f"{OUT_PATH}/hayato.db"

JST = pytz.timezone('Japan')

# Usages
# POINTS_USAGE = f"{COMMAND_PREFIX}points [add|total] <number...>"
