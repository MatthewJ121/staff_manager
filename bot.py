import discord
from discord.ext import commands
import os
import httpx
from dotenv import load_dotenv

guildID = [1328458609163763804] # guild id variable so commands update faster

load_dotenv() # load all the variables from the env file
bot = discord.Bot()
token = os.getenv('TOKEN')
roblox_api = os.getenv('roblox_api')


blgroups = [9688364, 10085029, 33263569, 34603205, 34549414, 34941244, 9927554]

## prints to console when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("the bot has awoken")
    

## list of extensions (classes), loads extensions
extnlist = [
    "resident",
    "staff"
]
for extn in extnlist:
    bot.load_extension(f"plugins.{extn}")

## runs the bot
bot.run(token)
#test