import os

import discord
import pytz
from dateutil import parser
from discord import app_commands, Interaction
from discord.abc import GuildChannel
from discord.errors import NotFound
from dotenv import load_dotenv

import src.logger as logger
from src import constants
from src.db.announcements.announcements_dao import announcements_dao
from src.errors import LoggedRuntimeError
from src.utils.announcements_util import AnnouncementsUtil

TAG = "client.py"

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if TOKEN is None:
    raise LoggedRuntimeError(TAG, "TOKEN not found. Check that .env file exists in src dir and that its contents are correct")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def send_wrapper(sender: Interaction | GuildChannel, text):
    logger.d(TAG, f"send: {text}")
    if isinstance(sender, Interaction):
        await sender.response.send_message(text)
    elif isinstance(sender, GuildChannel):
        await sender.send(text)


# async def send_wrapper(client: GuildChannel, text: str):
#     logger.d(TAG, f"send: {text}")
#     await client.send(text)

@tree.command(
    name="ping",
    description="ping",
    guild=discord.Object(391427484702212103)
)
async def ping(interaction: Interaction):
    logger.d(TAG, "ping")
    await send_wrapper(interaction, 'pong')


@tree.command(
    name="say",
    description="say",
    guild=discord.Object(391427484702212103)
)
async def say(interaction: Interaction, channel: str, message: str):
    logger.d(TAG, "say: " + message)
    try:
        channel_int = int(channel)
        logger.d(TAG, f"successfully casted channel to an int. channel_int: {channel_int}")
        guild_channel = await client.fetch_channel(channel_int)
        await send_wrapper(interaction, f"sending message: {message}")
        await send_wrapper(guild_channel, message)
    except ValueError as e:
        logger.e(TAG, e, f"failed to cast channel to an int. channel: {channel}")
        await send_wrapper(interaction, f"Could not find the specified channel: {channel}. Check the channel ID and try again.")
    except NotFound as e:
        logger.e(TAG, e, f"failed to cast channel to an int. channel: {channel}")
        await send_wrapper(interaction, f"Could not find the specified channel: {channel}. Check the channel ID and try again.")


@tree.command(
    name="schedule_announcement",
    description="schedule_announcement",
    guild=discord.Object(391427484702212103)
)
async def schedule_announcement(interaction: Interaction, time: str, channel: str, message: str):
    """

    TODO: Put in a db table with the following schema:
    ID:
    """
    logger.d(TAG, f"schedule_announcement: time: {time}, channel: {channel} message: {message}")

    try:
        parsed_time = parser.parse(time)
        if parsed_time.tzinfo is None:
            parsed_time = constants.JST.localize(parsed_time)
        # TODO: validate time parse

        channel_int = int(channel)
        logger.d(TAG, f"successfully casted channel to an int. channel_int: {channel_int}")
        await client.fetch_channel(channel_int)
        announcement = announcements_dao.schedule_announcement(parsed_time, channel_int, message)
        await send_wrapper(interaction, f"Will send the message at time: {parsed_time}. Announcement details: {announcement}")
    except ValueError as e:
        logger.e(TAG, e, f"failed to cast channel to an int. channel: {channel}")
        await send_wrapper(interaction, f"Could not find the specified channel: {channel}. Check the channel ID and try again. Announcement was not scheduled.")


# TODO: cancel announcement

# TODO: view all scheduled announcements

# TODO: view scheduled announcement by id


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=391427484702212103))
    announcements_util = AnnouncementsUtil(client)
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


client.run(TOKEN)
