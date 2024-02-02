import os
from typing import Optional

import discord
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
GUILD_IDS = os.getenv('GUILD_IDS').split(",")

guild_objects = []
for guild_id in GUILD_IDS:
    guild_objects.append(discord.Object(id=guild_id))

if TOKEN is None:
    raise LoggedRuntimeError(TAG, "TOKEN not found. Check that .env file exists in src dir and that its contents are correct")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def send_wrapper(sender: Interaction | GuildChannel, text: str, attachment_url: Optional[str] = None):
    logger.d(TAG, f"send_wrapper: text: {text}, attachment_url: {attachment_url}")
    if isinstance(sender, Interaction):
        await sender.response.send_message(text)
        if attachment_url is not None:
            await sender.response.send_message(attachment_url)
    elif isinstance(sender, GuildChannel):
        await sender.send(text)
        if attachment_url is not None:
            await sender.send(attachment_url)


def get_channel_id(channel: str) -> int:
    logger.d(TAG, f"get_channel_id: channel: {channel}")
    if channel.startswith("#"):
        logger.d(TAG, f"get_channel_id: channel starts with #. Removing it.")
        channel = channel[1:]
    if channel.startswith("<#") and channel.endswith(">"):
        logger.d(TAG, f"get_channel_id: channel starts with <# and ends with >. Removing them.")
        return int(channel[2:-1])
    resolved_channel = discord.utils.get(client.get_all_channels(), name=channel)
    if resolved_channel is not None:
        logger.d(TAG, f"get_channel_id: successfully resolved channel. resolved_channel: {resolved_channel}")
        return resolved_channel.id
    else:
        raise LoggedRuntimeError(TAG, f"Could not find the specified channel: {channel}. Check the channel name and try again.")


@tree.command(
    name="ping",
    description="ping",
    guilds=guild_objects,
)
@app_commands.default_permissions(administrator=True)
async def ping(interaction: Interaction):
    logger.d(TAG, "ping:")
    await send_wrapper(interaction, 'pong')


@tree.command(
    name="say",
    description="say",
    guilds=guild_objects
)
@app_commands.default_permissions(administrator=True)
async def say(interaction: Interaction, channel: str, message: str, attachment: Optional[discord.Attachment] = None):
    logger.d(TAG, f"say: channel: {channel}, message: {message}, attachment: {attachment}")
    try:
        channel_id = get_channel_id(channel)
        logger.d(TAG, f"say: successfully got channel id. channel_id: {channel_id}")
        guild_channel = await client.fetch_channel(channel_id)
        await send_wrapper(interaction, f"sending message to channel: {guild_channel}")
        await send_wrapper(guild_channel, message, attachment.url if attachment else None)
    except ValueError as e:
        logger.e(TAG, e, f"say: failed to cast channel to an int. channel: {channel}")
        await send_wrapper(interaction, f"Could not find the specified channel: {channel}. Check the channel ID and try again.")
    except NotFound as e:
        logger.e(TAG, e, f"say: failed to cast channel to an int. channel: {channel}")
        await send_wrapper(interaction, f"Could not find the specified channel: {channel}. Check the channel ID and try again.")
    except LoggedRuntimeError:
        await send_wrapper(interaction, f"Could not find the specified channel: {channel}. Check the channel name and try again.")


@tree.command(
    name="schedule_announcement",
    description="schedule_announcement",
    guilds=guild_objects
)
@app_commands.default_permissions(administrator=True)
async def schedule_announcement(interaction: Interaction, time: str, channel: str, message: str, attachment: Optional[discord.Attachment] = None):
    logger.d(TAG, f"schedule_announcement: time: {time}, channel: {channel} message: {message}, attachment: {attachment.url if attachment else 'None'}")
    try:
        parsed_time = parser.parse(time)
        if parsed_time.tzinfo is None:
            parsed_time = constants.JST.localize(parsed_time)
        # TODO: validate time parse

        channel_id = get_channel_id(channel)
        logger.d(TAG, f"schedule_announcement: successfully casted channel to an int. channel_id: {channel_id}")
        await client.fetch_channel(channel_id)
        announcement = announcements_dao.schedule_announcement(parsed_time, channel_id, message, attachment.url if attachment else None)
        await send_wrapper(interaction, f"Will send the message at time: {parsed_time}. Announcement details: {announcement}")
    except ValueError as e:
        logger.e(TAG, e, f"schedule_announcement: failed to parse time. time provided: {time}")
        await send_wrapper(interaction, f"Was not able to parse the provided time: {time}. Check the entered value and try again. Announcement was not scheduled.")


@tree.command(
    name="cancel_announcement",
    description="cancel_announcement",
    guilds=guild_objects
)
@app_commands.default_permissions(administrator=True)
async def cancel_announcement(interaction: Interaction, id: int):
    logger.d(TAG, f"cancel_announcement: id: {id}")
    announcement = announcements_dao.delete_announcement_by_id(id)
    if announcement is None:
        await send_wrapper(interaction, f"Could not find an announcement with the specified id: {id}.")
        return
    await send_wrapper(interaction, f"Announcement was canceled: {announcement}")


@tree.command(
    name="view_scheduled_announcements",
    description="view_scheduled_announcements",
    guilds=guild_objects
)
@app_commands.default_permissions(administrator=True)
async def view_scheduled_announcements(interaction: Interaction):
    logger.d(TAG, "view_scheduled_announcements:")
    announcements = announcements_dao.get_all_announcements()
    await send_wrapper(interaction, f"Found {len(announcements)} scheduled announcements:")
    channel = interaction.channel
    for announcement in announcements:
        await send_wrapper(channel, announcement)


@tree.command(
    name="view_announcement_by_id",
    description="view_announcement_by_id",
    guilds=guild_objects
)
@app_commands.default_permissions(administrator=True)
async def view_scheduled_announcement_by_id(interaction: Interaction, id: int):
    logger.d(TAG, f"view_scheduled_announcement_by_id: id: {id}")
    announcement = announcements_dao.get_announcement_by_id(id)
    if announcement is None:
        await send_wrapper(interaction, f"Could not find an announcement with the specified id: {id}.")
        return
    await send_wrapper(interaction, f"Found announcement: {announcement}")


@client.event
async def on_ready():
    for guild in guild_objects:
        await tree.sync(guild=guild)
    announcements_util = AnnouncementsUtil(client)
    logger.d(TAG, f"on_ready: announcements_util.is_started: {announcements_util.is_running}")
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
