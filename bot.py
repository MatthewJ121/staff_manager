import discord
from discord.ext import commands
import os
import httpx
httpx.Timeout(3)
from dotenv import load_dotenv
from datetime import datetime

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


"""
command: viewprofile
access: all users
input: username/id
front end: displays embed with basic user info, blacklist status, alt flags, and launches
back end: pulls information from roblox api and mongodb databases for relevant information, read only
"""
@bot.slash_command(guild_ids=guildID, name="viewprofile", description="View the profile of a user.")
async def profile(ctx, username: str):

    try:
        print(f"input is: {username}")
        uid = int(username) #checks if input is already a uid
        print("passed uid")
    except:
        # get player's uid if the entry is in string form
            try:
                 uid = httpx.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True}).json()["data"][0]["id"]
            except:
                 uid = 0 #wil cause user not found error in api

    # get player's profile from uid                      
    profile_ref = httpx.get("https://apis.roblox.com/cloud/v2/users/"+str(uid), headers={"x-api-key":(roblox_api)}).json()

    try: #handles ANY error, gives custom more readable message if error is no user found
        if profile_ref["code"] != "NOT_FOUND":#user not found
            error_embed = discord.Embed(
                 title = f'User "{username}" does not exist.',
                 description=
                 f"Check your spelling and try again",
                 color=discord.Color.orange())
        else:
            try:
                 error_embed = discord.Embed(#unrecognized error from API
                    title = f"API error: {profile_ref["code"]}",
                    description=
                    f"{profile_ref["message"]}\n"
                    f"Please **immediately** report this error to the launch host",
                    color = discord.Color.red())
            except:
                 error_embed = discord.Embed(#failure to retrieve API error, likely due to API being down
                    title = f"Uknown error",
                    description=
                    f"The Roblox API may be down, or another error has occured.\n"
                    f"Please **immediately** report this error to the launch host",
                    color = discord.Color.red())
        await ctx.respond(embed=error_embed)
    
    except: #if no error, gives user profile
        creationDate = datetime.strptime(profile_ref["createTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
        
        embed = discord.Embed(
            title=profile_ref["name"],
            description=
            f"Display Name: {profile_ref["displayName"]}\n"
            f"Account Age: {str(datetime.now() - creationDate).split(",")[0]}", 
            color=discord.Color.green())
        await ctx.respond(embed=embed)

# sends an embed message 
@bot.slash_command(guild_ids=guildID, name="embed", description="testing")
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