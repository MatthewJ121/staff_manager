import discord
from discord.ext import commands

class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    staffcmd = discord.SlashCommandGroup("management")
    @staffcmd.command(guild_ids=[1328458609163763804])
    async def test(self, ctx):
        await ctx.respond("this is a command in a cog and group")

def setup(bot):
    bot.add_cog(Staff(bot))