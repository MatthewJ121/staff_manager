import discord
from discord.ext import commands
import os
import requests
from dotenv import load_dotenv

load_dotenv() # load all the variables from the env file
bot = discord.Bot()
######################################################

guildID = [1328458609163763804]

######################################################

## prints when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is ready!")


## attempts to replicate viewprofile command from the other bot
@bot.slash_command(guild_ids=guildID, name="viewprofile", description="view the profile of a user")
async def profile(ctx, username: str):

    userid_request = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True}).json()["data"][0]["id"]
    profile_ref = requests.get(f"https://apis.roblox.com/cloud/v2/users/{userid_request}", headers={"x-api-key":os.getenv("roblox_api")}).json()

    embed = discord.Embed(title=profile_ref["name"], description="display name:"+profile_ref["displayName"]+" \n locale:"+profile_ref["locale"]+" \n createTime"+profile_ref["createTime"])
    await ctx.respond(embed=embed)

## checks latency
@bot.slash_command(guild_ids=guildID, name="ping", description="check latency")
async def ping(ctx):
    """
    replies with ping
    """
    await ctx.respond(f"your ping is {round(bot.latency * 1000)}ms")


## sends an embed message
@bot.slash_command(guild_ids=guildID, name="embed", description="my balls")
async def embed_test(ctx):
    """
   tests embeds
    """
    embed = discord.Embed(title="embed test", description="this is a test embed message", color=discord.Color.green())
    embed.add_field(name="field 1", value="value 1", inline=False)
    embed.set_footer(text="footer text")
    await ctx.respond(embed=embed)


## runs the bot
bot.run(os.getenv('token'))
#test