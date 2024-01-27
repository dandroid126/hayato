import src.logger as logger
from discord.ext import commands
import discord
from dotenv import load_dotenv
import os
import src.utils as utils
import src.constants as constants
from src.errors import LoggedRuntimeError

TAG = "client.py"

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if TOKEN is None:
    raise LoggedRuntimeError(TAG, "TOKEN not found. Check that .env file exists in src dir and that its contents are correct")

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=constants.COMMAND_PREFIX, description="Hayato Bot", intents=intents)


async def send_wrapper(context, text):
    logger.d(TAG, f"send: {text}")
    await context.send(text)


@bot.command()
async def ping(context):
    logger.d(TAG, "ping")
    await send_wrapper(context, 'pong')


@bot.command()
async def say(context, *args: str):
    logger.d(TAG, "make_comment: " + " ".join(args))
    await send_wrapper(context, " ".join(args))


@bot.event
async def on_ready():
    utils.ready_up()


bot.run(TOKEN)
