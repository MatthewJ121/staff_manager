import discord
import roblox
from roblox import Client
client = Client()
from discord.ext import commands
import os
from dotenv import load_dotenv

guildID = [1328458609163763804]

load_dotenv() # load all the variables from the env file
bot = discord.Bot()

## prints when the bot is ready
@bot.event
async def on_ready():
    #await bot.sync(guild=discord.Object(id=907125046793879602))
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is up!")

## currently just checks and returns username #TODO replace this with a sub command group
@bot.slash_command(guild_ids=guildID, description = "Search by username.")
async def viewprofile(ctx, username:str):
    user = await client.get_user_by_username(username=username)
    await ctx.respond(f"https://www.roblox.com/users/{user.id}/profile")

@bot.slash_command(guild_ids=guildID, description = "Search by ID.")
async def viewprofile2(ctx, user_id:int):
    try:
        user = await client.get_user(user_id)
        await ctx.respond(f"https://www.roblox.com/users/{user_id}/profile")
    except Exception as e:
        if e != "Invalid user.": #NOTE this doesnt work!!!!
            await ctx.respond(f"Unknown error! Please report this to a Superintendent.\n{e}")
        else:
            await ctx.respond("No user found. Please recheck your input.")


## sends an embed message
@bot.slash_command(guild_ids=guildID, description="test embed capabilities")
async def embed_test(ctx):
    embed = discord.Embed(title="embed test", description="this is a test embed message", color=discord.Color.green())
    embed.add_field(name="field 1", value="value 1", inline=False)
    embed.set_footer(text="footer text")
    await ctx.respond(embed=embed)


## runs the bot
bot.run(os.getenv('token'))