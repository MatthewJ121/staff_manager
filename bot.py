import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv() # load all the variables from the env file
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is ready!")

@bot.slash_command(guild_ids=[1328458609163763804], name="ping", description="check latency")
async def ping(ctx):
    """
    replies with ping
    """
    await ctx.respond(f"your ping is {round(bot.latency * 1000)}ms")


bot.run(os.getenv('token'))