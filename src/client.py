import os

import discord
from dateutil import parser
from discord.abc import GuildChannel
from discord.errors import NotFound
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv

import src.constants as constants
import src.logger as logger
from src.db.announcements.announcements_dao import announcements_dao
from src.errors import LoggedRuntimeError
from src.utils.announcements_util import AnnouncementsUtil

TAG = "client.py"

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if TOKEN is None:
    raise LoggedRuntimeError(TAG, "TOKEN not found. Check that .env file exists in src dir and that its contents are correct")

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=constants.COMMAND_PREFIX, description="Hayato Bot", intents=intents)


async def send_wrapper(sender: Context | GuildChannel, text):
    logger.d(TAG, f"send: {text}")
    await sender.send(text)


# async def send_wrapper(client: GuildChannel, text: str):
#     logger.d(TAG, f"send: {text}")
#     await client.send(text)

@bot.command()
async def ping(context):
    logger.d(TAG, "ping")
    await send_wrapper(context, 'pong')


@bot.command()
async def say(context, channel: str, *message: str):
    logger.d(TAG, "say: " + " ".join(message))
    try:
        channel_int = int(channel)
        logger.d(TAG, f"successfully casted channel to an int. channel_int: {channel_int}")
        guild_channel = await bot.fetch_channel(channel_int)
        await send_wrapper(guild_channel, ' '.join(message))
    except ValueError as e:
        logger.e(TAG, e, f"failed to cast channel to an int. channel: {channel}")
        await send_wrapper(context, f"Could not find the specified channel: {channel}. Check the channel ID and try again.")
    except NotFound as e:
        logger.e(TAG, e, f"failed to cast channel to an int. channel: {channel}")
        await send_wrapper(context, f"Could not find the specified channel: {channel}. Check the channel ID and try again.")


@bot.command()
async def schedule_announcement(context, time: str, channel: str, *message: str):
    """

    TODO: Put in a db table with the following schema:
    ID:
    """
    logger.d(TAG, f"schedule_announcement: time: {time}, channel: {channel} message: {' '.join(message)}")

    try:
        parsed_time = parser.parse(time)
        # TODO: validate time parse

        channel_int = int(channel)
        logger.d(TAG, f"successfully casted channel to an int. channel_int: {channel_int}")
        await bot.fetch_channel(channel_int)
        announcement = announcements_dao.schedule_announcement(parsed_time, channel_int, ' '.join(message))
        await send_wrapper(context, f"Will send the message at time: {parsed_time}. Announcement details: {announcement}")
    except ValueError as e:
        logger.e(TAG, e, f"failed to cast channel to an int. channel: {channel}")
        await send_wrapper(context, f"Could not find the specified channel: {channel}. Check the channel ID and try again. Announcement was not scheduled.")


# TODO: cancel announcement

# TODO: view all scheduled announcements

# TODO: view scheduled announcement by id


@bot.event
async def on_ready():
    announcements_util = AnnouncementsUtil(bot)
    logger.d(TAG, f"ready_up: announcements_util.is_started: {announcements_util.is_running}")
    # TODO: Add something like this once there is a way to have multiple threads listening for the interrupt signal.
    # loop = asyncio.get_running_loop()
    # threading.Thread(target=bot_logout_listener, args=(loop, )).start()


# def bot_logout_listener(loop):
#     logger.d(TAG, "bot_logout_listener")
#     while not signal_util.is_interrupted:
#         logger.d(TAG, "bot_logout_listener: not interrupted. sleeping for 60 seconds")
#         signal_util.wait(60)
#     logger.d(TAG, "bot_logout_listener: shutting down")
#     asyncio.run_coroutine_threadsafe(bot.close(), loop)


bot.run(TOKEN)
