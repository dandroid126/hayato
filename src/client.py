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
from src.constants import LOGGER
from src.db.announcements.announcements_dao import announcements_dao
from src.db.birthday.birthday_dao import birthday_dao
from src.errors import LoggedRuntimeError
from src.utils.announcements_util import AnnouncementsUtil
from src.utils.birthday_util import BirthdayUtil

TAG = "client.py"

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))
BIRTHDAY_CHANNEL_ID = os.getenv('BIRTHDAY_CHANNEL_ID')
BIRTHDAY_CHANNEL_ID = int(BIRTHDAY_CHANNEL_ID) if BIRTHDAY_CHANNEL_ID is not None else None
REQUESTS_CHANNEL_ID = os.getenv('REQUESTS_CHANNEL_ID')
REQUESTS_CHANNEL_ID = int(REQUESTS_CHANNEL_ID) if REQUESTS_CHANNEL_ID is not None else None
REQUESTS_USERS = os.getenv('REQUESTS_USERS')
REQUESTS_USERS = REQUESTS_USERS.split(",") if REQUESTS_USERS else None
announcements_util: Optional[AnnouncementsUtil] = None
birthday_util: Optional[BirthdayUtil] = None

guild_object = discord.Object(id=GUILD_ID)

if TOKEN is None:
    raise LoggedRuntimeError(TAG, "TOKEN not found. Check that .env file exists in src dir and that its contents are correct")

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def send_wrapper(sender: Interaction | GuildChannel, text: str, attachment: Optional[discord.Attachment] = None, ephemeral: Optional[bool] = False):
    LOGGER.d(TAG, f"send_wrapper: text: {text}, attachment: {attachment}")
    file = await attachment.to_file() if attachment is not None else MISSING
    texts = []
    while len(text) >= 2000:
        texts.append(text[:2000])
        text = text[2000:]
    texts.append(text)
    if isinstance(sender, Interaction):
        await sender.response.send_message(texts[0], file=file, ephemeral=ephemeral)
        for text in texts[1:]:
            await sender.followup.send(text)
    elif isinstance(sender, GuildChannel):
        await sender.send(texts[0], file=file)
        for text in texts[1:]:
            await sender.send(text)


def replace_line_breaks(text: str) -> str:
    LOGGER.d(TAG, f"replace_line_breaks: text: {text}")
    return text.replace("\\n", "\n")


# This is commented out because it should not go live. It is convenient to have a test command for development purposes, so it will stay here commented out.
# @tree.command(
#     name="command_test",
#     description="command_test",
#     guild=guild_object
# )
# @app_commands.default_permissions(administrator=True)
# async def command_test(interaction: discord.Interaction, message: str):
#     LOGGER.d(TAG, "test:")
#     await send_wrapper(interaction, 'test')


@tree.command(
    name="say",
    description="Say something in a channel now",
    guild=guild_object
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
    guild=guild_object
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
        LOGGER.e(TAG, f"schedule_announcement: failed to parse time. time provided: {time}", e)
        await send_wrapper(interaction, f"Was not able to parse the provided time: {time}. Check the entered value and try again. Announcement was not scheduled.")


@tree.command(
    name="cancel_announcement",
    description="Cancel Announcement by ID",
    guild=guild_object
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
    guild=guild_object
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
    guild=guild_object
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
    guild=guild_object
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
    guild=guild_object
)
@app_commands.default_permissions(administrator=True)
async def get_all_responses(interaction: discord.Interaction):
    LOGGER.d(TAG, "get_all_responses:")
    await send_wrapper(interaction, responses.get_responses_file())

if BIRTHDAY_CHANNEL_ID is not None:
    @tree.command(
        name="learn_birthday",
        description="Tell me your birthday, and I will send you happy birthday wishes.",
        guild=guild_object
    )
    async def learn_birthday(interaction: discord.Interaction, date: str):
        LOGGER.d(TAG, "learn_birthday:")
        user_id = interaction.user.id

        try:
            parsed_date = parser.parse(date).strftime("%m-%d")
            LOGGER.d(TAG, f"learn_birthday: user_id: {user_id}, parsed_date: {parsed_date}")
            birthday = birthday_dao.learn_birthday(user_id, parsed_date)
            await send_wrapper(interaction, "I will remember that your birthday is on this day: " + birthday.date.strftime("%B %d"))
        except ValueError as e:
            LOGGER.e(TAG, f"learn_birthday: failed to parse date. date provided: {date}", e)
            await send_wrapper(interaction, f"Sorry, I was not able to understand the date: '{date}'. Please try again in the format 'January 1st'.")


if BIRTHDAY_CHANNEL_ID is not None:
    @tree.command(
        name="learn_others_birthday",
        description="Tell me someone's birthday, and I will send them happy birthday wishes.",
        guild=guild_object
    )
    async def learn_others_birthday(interaction: discord.Interaction, user: discord.User, date: str):
        LOGGER.d(TAG, "learn_birthday:")
        user_id = user.id

        try:
            parsed_date = parser.parse(date).strftime("%m-%d")
            LOGGER.d(TAG, f"learn_birthday: user_id: {user_id}, parsed_date: {parsed_date}")
            birthday = birthday_dao.learn_birthday(user_id, parsed_date)
            await send_wrapper(interaction, f"I will remember that {user.mention}'s birthday is on this day: " + birthday.date.strftime("%B %d"))
        except ValueError as e:
            LOGGER.e(TAG, f"learn_birthday: failed to parse date. date provided: {date}", e)
            await send_wrapper(interaction, f"Sorry, I was not able to understand the date: '{date}'. Please try again in the format 'January 1st'.")


if BIRTHDAY_CHANNEL_ID is not None:
    @tree.command(
        name="forget_birthday",
        description="I will no longer send you happy birthday wishes. :(",
        guild=guild_object
    )
    async def forget_birthday(interaction: discord.Interaction):
        LOGGER.d(TAG, "forget_birthday:")
        user_id = interaction.user.id
        LOGGER.d(TAG, f"forget_birthday: user_id: {user_id}")
        birthday_dao.forget_birthday(user_id)
        await send_wrapper(interaction, "Your birthday has been forgotten.")


if BIRTHDAY_CHANNEL_ID is not None:
    @tree.command(
        name="get_all_birthdays",
        description="Get all the birthdays",
        guild=guild_object
    )
    @app_commands.default_permissions(administrator=True)
    async def get_all_birthdays(interaction: discord.Interaction):
        LOGGER.d(TAG, "get_all_birthdays:")
        birthdays = birthday_dao.get_all_birthdays()
        response = "Birthdays:\n"
        for birthday in birthdays:
            response += f"username: {client.get_user(birthday.user_id)}: date: {birthday.date.strftime('%m/%d')}\n"
        await send_wrapper(interaction, response)

if REQUESTS_CHANNEL_ID is not None:
    @tree.command(
        name="request",
        description="Have HAYATO send a request that only you and the Sensei can see.",
        guild=guild_object
    )
    async def send_request(interaction: discord.Interaction, request: str):
        LOGGER.d(TAG, f"request:: {request}")
        channel = client.get_channel(REQUESTS_CHANNEL_ID)
        message = f"user: {interaction.user.name}, request: {request}"
        if REQUESTS_USERS:
            for role_or_user_id in REQUESTS_USERS:
                if role_or_user_id.startswith('&'):
                    # ID is a role ID
                    role_id = int(role_or_user_id[1:])
                    guild = client.get_guild(GUILD_ID)
                    role = guild.get_role(role_id) if guild else None
                    message += f" {role.mention}" if role else ""
                else:
                    # ID is a user ID
                    try:
                        user_id = int(role_or_user_id)
                        user = client.get_user(user_id)
                        message += f" {user.mention}"
                    except ValueError as e:
                        LOGGER.e(TAG, "'id' could not be casts to an int to make it into a user ID.", e)
        await send_wrapper(channel, message)
        await send_wrapper(interaction, "OHAYAHO!! THE SENSEI HAVE RECEIVED YOUR REQUEST!!!", ephemeral=True)


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        LOGGER.d(TAG, f"on_message: message.author == client.user: {message.author == client.user}")
        return
    if message.guild.id != GUILD_ID:
        LOGGER.d(TAG, f"on_message: message.guild.id: {message.guild.id} not equal to GUILD_ID: {GUILD_ID}")
        return
    msg = message.content
    response = responses.get_response(msg)
    if response:
        await message.channel.send(response)


@client.event
async def on_ready():
    LOGGER.d(TAG, "on_ready:")
    global announcements_util
    global birthday_util
    await tree.sync(guild=guild_object)
    if announcements_util is None or not announcements_util.is_running:
        # Start waiting for announcement scheduled time
        announcements_util = AnnouncementsUtil(client)
        LOGGER.d(TAG, f"on_ready: announcements_util.is_started: {announcements_util.is_running}")
    else:
        # If the announcements util is already set, skip setting it again
        # This happens in the case of a reconnect
        LOGGER.d(TAG, "on_ready: announcements_util is already started")

    # If the birthdays channel is set, start waiting for birthdays
    if BIRTHDAY_CHANNEL_ID is not None and (birthday_util is None or not birthday_util.is_running):
        birthday_util = BirthdayUtil(client, BIRTHDAY_CHANNEL_ID)
        LOGGER.d(TAG, f"on_ready: birthday_util.is_started: {birthday_util.is_running}")
    else:
        # If the birthday util is already set, skip setting it again
        # This happens in the case of a reconnect
        LOGGER.d(TAG, "on_ready: birthday_util is already started")

    LOGGER.d(TAG, "on_ready: done")

client.run(TOKEN, reconnect=True)
