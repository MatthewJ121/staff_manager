import os
import discord
import datetime
import time
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
        await ctx.defer()

        start = time.perf_counter()
        if username == None:
            username = ctx.author.display_name

        #request profile and thumbnail from global
        profile_ref = None
        profile_img = None
        try:
            profile_ref = await get_robloxprofile(username)
        except Exception as e:
            error_embed = discord.Embed(title="An error occured",description=e,color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
        
        async with httpx.AsyncClient() as client:
            profile_img = await get_picture(profile_ref["id"])
            await client.aclose()
            
        async with httpx.AsyncClient() as client:
            so_ranks = await get_rank(profile_ref["id"],"so")
            await client.aclose()

        #create and send embed
        launch_count = get_db(profile_ref["id"],"rdb")
        embed = discord.Embed(
            title=profile_ref["name"],
            color=discord.Color.dark_green(),
            thumbnail=profile_img
            )
        embed.add_field(name="Display Name",value=profile_ref['displayName'], inline=True)
        embed.add_field(name="Date Created",value=(datetime.datetime.fromisoformat(profile_ref['createTime'])).strftime('%m/%d/%Y'),inline=True)
        
        if so_ranks != None:
            if 32941073 in so_ranks:
                rstr = so_ranks[32941073]["name"]
            else:
                rstr = "Visitor"
            if 8294909 in so_ranks:
                if so_ranks[8294909]["name"] not in rstr:
                    rstr = rstr + "\n" + so_ranks[8294909]["name"]
            if 8294866 in so_ranks:
                if so_ranks[8294866]["name"] not in rstr:
                    rstr = rstr + "\n" + so_ranks[8294866]["name"]
            if 10021698 in so_ranks:
                if so_ranks[10021698]["name"] not in rstr:
                    rstr = rstr + "\n" + so_ranks[10021698]["name"]
            embed.add_field(name="Ranks",value=rstr,inline=False)
            
        if launch_count != None:
            embed.add_field(name="Launches Attended",value=int(launch_count["launches"]),inline=False)
        else:
            embed.add_field(name="Launches Attended",value=0,inline=False)

        end = time.perf_counter()
        embed.set_footer(text=f"Command took {round(end-start,3)}s to complete.")
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Resident(bot))