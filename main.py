import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
description = "The Revival of Mikebot"
version = 2.0
bot = commands.Bot(command_prefix=commands.when_mentioned_or('?'), description=description, intents=intents)

initial_extensions = ['cogs.moderation','cogs.owner','cogs.fun']
if __name__ == __name__: # loading the cogs
    for extension in initial_extensions:
        bot.load_extension(extension)


@bot.event
async def on_ready():
    print(f"{bot.user.name} is now running on discord.py version {discord.__version__}")
    activity = discord.Activity(type=discord.ActivityType.watching, name="sully generate scream energy")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    help_command = bot.get_command('help')
    help_command.hidden = True

bot.run(TOKEN)
