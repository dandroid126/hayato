import os
from typing import Optional

import discord
from dateutil import parser
from discord import app_commands
from discord.abc import GuildChannel
from discord.interactions import Interaction
from discord.utils import MISSING
from dotenv import load_dotenv

import src.utils.responses as responses
from src import constants
from src.db.announcements.announcements_dao import announcements_dao
from src.errors import LoggedRuntimeError
from src.utils.announcements_util import AnnouncementsUtil
from src.constants import LOGGER

TAG = "client.py"

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_IDS = os.getenv('GUILD_IDS').split(",")

guild_objects = []
for guild_id in GUILD_IDS:
    guild_objects.append(discord.Object(id=guild_id))

if TOKEN is None:
    raise LoggedRuntimeError(TAG, "TOKEN not found. Check that .env file exists in src dir and that its contents are correct")

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def send_wrapper(sender: Interaction | GuildChannel, text: str, attachment: Optional[discord.Attachment] = None):
    LOGGER.d(TAG, f"send_wrapper: text: {text}, attachment: {attachment}")
    file = await attachment.to_file() if attachment is not None else MISSING
    if isinstance(sender, Interaction):
        await sender.response.send_message(text, file=file)
    elif isinstance(sender, GuildChannel):
        await sender.send(text, file=file)


def replace_line_breaks(text: str) -> str:
    LOGGER.d(TAG, f"replace_line_breaks: text: {text}")
    return text.replace("\\n", "\n")


# This is commented out because it should not go live. It is convenient to have a test command for development purposes, so it will stay here commented out.
# @tree.command(
#     name="command_test",
#     description="command_test",
#     guilds=guild_objects
# )
# @app_commands.default_permissions(administrator=True)
# async def command_test(interaction: discord.Interaction, message: str):
#     LOGGER.d(TAG, "test:")
#     await send_wrapper(interaction, 'test')


@tree.command(
    name="say",
    description="Say something in a channel now",
    guilds=guild_objects
)
@app_commands.default_permissions(administrator=True)
async def say(interaction: discord.Interaction, channel: discord.TextChannel, message: str, attachment: Optional[discord.Attachment] = None):
    LOGGER.d(TAG, f"say: channel: {channel}, message: {message}, attachment: {attachment}")
    message = replace_line_breaks(message)
    await send_wrapper(interaction, f"sending message to channel: {channel}", attachment)
    await send_wrapper(channel, message, attachment)


@tree.command(
    name="schedule_announcement",
    description="Schedule Announcement",
    guilds=guild_objects
)
@app_commands.default_permissions(administrator=True)
async def schedule_announcement(interaction: discord.Interaction, time: str, channel: discord.TextChannel, message: str, attachment: Optional[discord.Attachment] = None):
    LOGGER.d(TAG, f"schedule_announcement: time: {time}, channel: {channel} message: {message}, attachment: {attachment}")
    message = replace_line_breaks(message)
    try:
        parsed_time = parser.parse(time)
        if parsed_time.tzinfo is None:
            parsed_time = constants.JST.localize(parsed_time)
        announcement = announcements_dao.schedule_announcement(parsed_time, channel.id, message, attachment.to_dict() if attachment else None)
        await send_wrapper(interaction, f"Will send the message at time: {parsed_time}. Announcement details: {announcement}")
    except ValueError as e:
        LOGGER.e(TAG, e, f"schedule_announcement: failed to parse time. time provided: {time}")
        await send_wrapper(interaction, f"Was not able to parse the provided time: {time}. Check the entered value and try again. Announcement was not scheduled.")


@tree.command(
    name="cancel_announcement",
    description="Cancel Announcement by ID",
    guilds=guild_objects
)
@app_commands.default_permissions(administrator=True)
async def cancel_announcement(interaction: discord.Interaction, announcement_id: int):
    LOGGER.d(TAG, f"cancel_announcement: announcement_id: {announcement_id}")
    announcement = announcements_dao.delete_announcement_by_id(announcement_id)
    if announcement is None:
        await send_wrapper(interaction, f"Could not find an announcement with the specified id: {announcement_id}.")
        return
    await send_wrapper(interaction, f"Announcement was canceled: {announcement}")


@tree.command(
    name="view_scheduled_announcements",
    description="View All Scheduled Announcements",
    guilds=guild_objects
)
@app_commands.default_permissions(administrator=True)
async def view_scheduled_announcements(interaction: discord.Interaction):
    LOGGER.d(TAG, "view_scheduled_announcements:")
    announcements = announcements_dao.get_all_announcements()
    await send_wrapper(interaction, f"Found {len(announcements)} scheduled announcements:")
    channel = interaction.channel
    for announcement in announcements:
        await send_wrapper(channel, announcement)


@tree.command(
    name="view_announcement_by_id",
    description="View Scheduled Announcement by ID",
    guilds=guild_objects
)
@app_commands.default_permissions(administrator=True)
async def view_scheduled_announcement_by_id(interaction: discord.Interaction, announcement_id: int):
    LOGGER.d(TAG, f"view_scheduled_announcement_by_id: announcement_id: {announcement_id}")
    announcement = announcements_dao.get_announcement_by_id(announcement_id)
    if announcement is None:
        await send_wrapper(interaction, f"Could not find an announcement with the specified id: {announcement_id}.")
        return
    await send_wrapper(interaction, f"Found announcement: {announcement}")


@tree.command(
    name="reload_responses",
    description="Reload the responses file",
    guilds=guild_objects
)
@app_commands.default_permissions(administrator=True)
async def reload_responses(interaction: discord.Interaction):
    LOGGER.d(TAG, "reload_responses:")
    if responses.load_responses_file():
        await send_wrapper(interaction, "Responses file was reloaded.")
    else:
        await send_wrapper(interaction, "Failed to reload responses file. Please check the format and try again. No changes were made.")


@tree.command(
    name="get_all_responses",
    description="Get the contents of the responses file",
    guilds=guild_objects
)
@app_commands.default_permissions(administrator=True)
async def get_all_responses(interaction: discord.Interaction):
    LOGGER.d(TAG, "get_all_responses:")
    await send_wrapper(interaction, responses.get_responses_file())


@client.event
async def on_message(message: discord.Message):
    if not any(message.guild.id == guild.id for guild in guild_objects):
        LOGGER.d(TAG, f"on_message: message.guild.id: {message.guild.id} not in guild_objects: {guild_objects}")
        return
    if message.author == client.user:
        LOGGER.d(TAG, f"on_message: message.author == client.user: {message.author == client.user}")
        return
    msg = message.content
    response = responses.get_response(msg)
    if response:
        await message.channel.send(response)


@client.event
async def on_ready():
    for guild in guild_objects:
        await tree.sync(guild=guild)
    announcements_util = AnnouncementsUtil(client)
    LOGGER.d(TAG, f"on_ready: announcements_util.is_started: {announcements_util.is_running}")
    # TODO: Add something like this once there is a way to have multiple threads listening for the interrupt signal.
    # loop = asyncio.get_running_loop()
    # threading.Thread(target=bot_logout_listener, args=(loop, )).start()


# def bot_logout_listener(loop):
#     LOGGER.d(TAG, "bot_logout_listener")
#     while not signal_util.is_interrupted:
#         LOGGER.d(TAG, "bot_logout_listener: not interrupted. sleeping for 60 seconds")
#         signal_util.wait(60)
#     LOGGER.d(TAG, "bot_logout_listener: shutting down")
#     asyncio.run_coroutine_threadsafe(bot.close(), loop)


client.run(TOKEN)
