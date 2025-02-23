import os
import discord
from discord.ext import commands
from plugins.globalfx import *
roblox_api = os.getenv('roblox_api')


class Resident(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    
    """
    command: viewprofile
    access: all users
    input: username/id
    front end: displays embed with basic user info, blacklist status, alt flags, and launches
    back end: pulls information from roblox api and mongodb databases for relevant information, read only
    """
    @commands.slash_command(guild_ids=[1328458609163763804])
    async def viewprofile(self, ctx, username: str = None):
        if username == None:
            username = ctx.author.display_name

        profile_ref = None
        try:
            profile_ref = await get_robloxprofile(username)
        except Exception as e:
            error_embed = discord.Embed(title="An error occured",description=e,color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
        
        await ctx.defer()
        embed = discord.Embed(
            title=profile_ref["name"],
            description="Display Name: "+profile_ref["displayName"]+" \n Locale: "+profile_ref["locale"]+" \n Date Created: "+profile_ref["createTime"], color=discord.Color.green())
        await ctx.respond(embed=embed)
        

def setup(bot):
    bot.add_cog(Resident(bot))