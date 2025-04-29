import discord
from discord.ext import commands
import os
import httpx
from dotenv import load_dotenv

load_dotenv() # load all the variables from the env file
bot = discord.Bot(debug_guilds=[1328458609163763804])
token = os.getenv('TOKEN')
roblox_api = os.getenv('roblox_api')

from plugins.globalfx import *
## prints to console when the bot is ready
@bot.event
async def on_ready():
    print(f"\033[94mLogged in as {bot.user} (ID: {bot.user.id})\033[0m")
    

## list of extensions (classes), loads extensions
extnlist = [
    "resident",
    "staff",
    "blacklists"
]
for extn in extnlist:
    bot.load_extension(f"plugins.{extn}")

## runs the bot
bot.run(token)
#test