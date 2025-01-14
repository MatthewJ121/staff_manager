import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv() # load all the variables from the env file
bot = discord.Bot()

######################################################

guildID = 1328458609163763804

######################################################

# prints when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is ready!")

# attempts to replicate viewprofile command from the other bot
@bot.slash_command(guild_ids=[1328458609163763804], name="viewprofile", description="view the profile of a user")
async def profile(ctx, *, username: str):

    await ctx.respond(f"Username: {username}")
   
# checks latency
@bot.slash_command(guild_ids=[1328458609163763804], name="ping", description="check latency")
async def ping(ctx):
    """
    replies with ping
    """
    await ctx.respond(f"your ping is {round(bot.latency * 1000)}ms")

# sends an embed message
@bot.slash_command(guild_ids=[1328458609163763804], name="embed", description="test embed capabilities")
async def embed_test(ctx):
    """
   tests embeds
    """
    embed = discord.Embed(title="embed test", description="this is a test embed message", color=discord.Color.green())
    embed.add_field(name="field 1", value="value 1", inline=False)
    embed.set_footer(text="footer text")
    await ctx.respond(embed=embed)

bot.run(os.getenv('token'))
#test