import os
from typing import Optional

import discord
from dateutil import parser
from discord import app_commands
from discord.abc import GuildChannel
from dotenv import load_dotenv

import src.logger as logger
import src.utils.responses as responses
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

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def send_wrapper(sender: discord.Interaction | GuildChannel, text: str, attachment_url: Optional[str] = None):
    logger.d(TAG, f"send_wrapper: text: {text}, attachment_url: {attachment_url}")
    if isinstance(sender, discord.Interaction):
        await sender.response.send_message(text)
        if attachment_url is not None:
            await sender.response.send_message(attachment_url)
    elif isinstance(sender, GuildChannel):
        await sender.send(text)
        if attachment_url is not None:
            await sender.send(attachment_url)


def replace_line_breaks(text: str) -> str:
    logger.d(TAG, f"replace_line_breaks: text: {text}")
    return text.replace("\\n", "\n")


# This is commented out because it should not go live. It is convenient to have a test command for development purposes, so it will stay here commented out.
# @tree.command(
#     name="command_test",
#     description="command_test",
#     guilds=guild_objects
# )
# @app_commands.default_permissions(administrator=True)
# async def command_test(interaction: discord.Interaction, message: str):
#     logger.d(TAG, "test:")
#     await send_wrapper(interaction, 'test')


@tree.command(
    name="say",
    description="Say something in a channel now",
    guilds=guild_objects
)
@app_commands.default_permissions(administrator=True)
async def say(interaction: discord.Interaction, channel: discord.TextChannel, message: str, attachment: Optional[discord.Attachment] = None):
    logger.d(TAG, f"say: channel: {channel}, message: {message}, attachment: {attachment}")
    message = replace_line_breaks(message)
    await send_wrapper(interaction, f"sending message to channel: {channel}")
    await send_wrapper(channel, message, attachment.url if attachment else None)


@tree.command(
    name="schedule_announcement",
    description="Schedule Announcement",
    guilds=guild_objects
)
@app_commands.default_permissions(administrator=True)
async def schedule_announcement(interaction: discord.Interaction, time: str, channel: discord.TextChannel, message: str, attachment: Optional[discord.Attachment] = None):
    logger.d(TAG, f"schedule_announcement: time: {time}, channel: {channel} message: {message}, attachment: {attachment.url if attachment else 'None'}")
    message = replace_line_breaks(message)
    try:
        parsed_time = parser.parse(time)
        if parsed_time.tzinfo is None:
            parsed_time = constants.JST.localize(parsed_time)
        announcement = announcements_dao.schedule_announcement(parsed_time, channel.id, message, attachment.url if attachment else None)
        await send_wrapper(interaction, f"Will send the message at time: {parsed_time}. Announcement details: {announcement}")
    except ValueError as e:
        logger.e(TAG, e, f"schedule_announcement: failed to parse time. time provided: {time}")
        await send_wrapper(interaction, f"Was not able to parse the provided time: {time}. Check the entered value and try again. Announcement was not scheduled.")


@tree.command(
    name="cancel_announcement",
    description="Cancel Announcement by ID",
    guilds=guild_objects
)
@app_commands.default_permissions(administrator=True)
async def cancel_announcement(interaction: discord.Interaction, announcement_id: int):
    logger.d(TAG, f"cancel_announcement: announcement_id: {announcement_id}")
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
    logger.d(TAG, "view_scheduled_announcements:")
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
    logger.d(TAG, f"view_scheduled_announcement_by_id: announcement_id: {announcement_id}")
    announcement = announcements_dao.get_announcement_by_id(announcement_id)
    if announcement is None:
        await send_wrapper(interaction, f"Could not find an announcement with the specified id: {announcement_id}.")
        return
    await send_wrapper(interaction, f"Found announcement: {announcement}")


@client.event
async def on_message(message):
    if message.author == client.user:
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
