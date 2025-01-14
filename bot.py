import discord
import roblox
from roblox import Client
client = Client()
from discord.ext import commands
import os
import httpx
from dotenv import load_dotenv
import datetime

date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
current_date = datetime.datetime.now()
print(f"date is {current_date}")

guildID = [1328458609163763804]

load_dotenv() # load all the variables from the env file
bot = discord.Bot()

## prints when the bot is ready
@bot.event
async def on_ready():
    #await bot.sync(guild=discord.Object(id=907125046793879602))
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is ready!")


## attempts to replicate viewprofile command from the other bot
@bot.slash_command(guild_ids=guildID, description="view the profile of a user")
async def viewprofile(ctx, username: str):

    userid_request = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True}).json()["data"]
    profile_ref = requests.get(f"https://apis.roblox.com/cloud/v2/users/{userid_request}", headers={"x-api-key":os.getenv("roblox_api")}).json()
  
    creation_date = datetime.datetime.strptime(profile_ref["createTime"], date_format)
    print(f"AGHHJHHHHHH{creation_date}")
    creation_date = str(creation_date[0:creation_date.index(" ")])
    print(creation_date)
    embed = discord.Embed(
        title=profile_ref["name"], 
        description=
        "Display name: " + profile_ref["displayName"] +
        "\n ID :" + profile_ref["id"] + 
        "\n Age: " + (current_date - creation_date))
    await ctx.respond(embed=embed)

## sends an embed message
@bot.slash_command(guild_ids=guildID, description="test embed capabilities")
async def embed_test(ctx):
    embed = discord.Embed(title="embed test", description="this is a test embed message", color=discord.Color.green())
    embed.add_field(name="field 1", value="value 1", inline=False)
    embed.set_footer(text="footer text")
    await ctx.respond(embed=embed)

## runs the bot
bot.run(os.getenv('token'))