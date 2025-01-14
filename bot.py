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

### MongoDB Handling ###

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = (os.getenv('URI'))
mongoclient = MongoClient(uri)
rdb = mongoclient.SilverOaks.ResidentList
bdb = mongoclient.SilverOaks.Blacklist
sdb = mongoclient.SilverOaks.StaffTracker

blgroups = [9688364, 10085029, 33263569, 34603205, 34549414, 34941244, 9927554]

### ###


## prints to console when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("the bot has awoken")


## attempts to replicate viewprofile command from the other bot
@bot.slash_command(guild_ids=guildID, name="viewprofile", description="View the profile of a user.")
async def profile(ctx, username: str):

    # get player's uid from their name, handle if no name found
    userid_request = httpx.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True}).json()["data"]

    if len(userid_request) == 0:
        error_embed = discord.Embed(title="No User Found",description=f"There is no user with the name **{username}**.\nCheck your spelling and try again.",color=discord.Color.red())
        await ctx.respond(embed=error_embed)
        return

    # get player's profile from uid                      
    profile_ref = httpx.get("https://apis.roblox.com/cloud/v2/users/"+str(userid_request[0]["id"]), headers={"x-api-key":(roblox_api)}).json()

    embed = discord.Embed(
        title=profile_ref["name"],
        description="Display Name: "+profile_ref["displayName"]+" \n Locale: "+profile_ref["locale"]+" \n Date Created: "+profile_ref["createTime"], color=discord.Color.green())
    await ctx.respond(embed=embed)

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
bot.run(token)
#test