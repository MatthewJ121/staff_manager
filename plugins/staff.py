import os
import discord
import bot
import datetime
import json
from discord.ext import commands
from plugins.globalfx import *
roblox_api = os.getenv('roblox_api')

class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    staffcmd = discord.SlashCommandGroup("mgmt")
    """
    command: discipline
    access: mgmt
    input: username/reason/length(#launches)
    front end: suspends x player w/ confirmation modal
    back end: adds x player to suspension DB, removes appropriate ranks (if length > 0), if executor does not have director rank, only issues warnings
    """
    @staffcmd.command(description="Issues a punishment to the staff member.",guild_ids=[1328458609163763804])
    @commands.has_any_role(1359813138983157854,1359804131828564028)
    async def discipline(self, ctx, username: discord.Member, reason: str, length: int):
        await ctx.defer()

        profile_ref = None
        try:
            profile_ref = await get_robloxprofile(username.display_name)
        except Exception as e:
            error_embed = discord.Embed(title="An error occured",description=e,color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)

        rank = await get_rank(profile_ref["id"],"so")
        suspension_profile = susdb.find_one({"userid": profile_ref["id"], "active": True})

        # checks
        if suspension_profile == None and rank != {}:
            # if player's rank is above resident and below FS
            # or if the player is FS and the executor is a director
            if (rank[32941073]["rank"] > 11 and rank[32941073]["rank"] < 25) or (rank[32941073]["rank"] == 25 and any(role.id == 1359804131828564028 for role in ctx.author.roles)):
                picture = None
            
                async with httpx.AsyncClient() as client:
                    picture = await get_picture(profile_ref["id"])
                await client.aclose()

                check_embed = discord.Embed(title="Is this the right person?",color=discord.Color.blurple())
                check_embed.set_thumbnail(url=picture)
                check_embed.add_field(name="Employee",value=profile_ref["name"],inline=True)
                check_embed.add_field(name="Issuer", value=ctx.author.display_name,inline=True)
                check_embed.add_field(name="Reason",value=reason,inline=False)

                suspension = False
                if length > 0 and any(role.id == 1359804131828564028 for role in ctx.author.roles):
                    check_embed.add_field(name="Duration",value=str(length)+" Launches",inline=False)
                    suspension = True

                # auto dm
                message_embed = discord.Embed(title="Notice of Disciplinary Action?",color=discord.Color.dark_red())

                class check_view(discord.ui.View):
                    def __init__(self): # refer to coconut.png
                        super().__init__()
                        self.value = None

                    @discord.ui.button(label="Yes",emoji="✅")
                    async def yes_callback(self, button: discord.ui.Button, ctx2):
                        # handle yes

                        # log it
                        start_embed = check_embed
                        if suspension:
                            start_embed.title = "Suspension Issued"
                            start_embed.color = discord.Color.dark_red()
                        else:
                            start_embed.title = "Warning Issued"
                            start_embed.color = discord.Color.dark_orange()
                        await bot.bot.get_channel(1359454889704427603).send(embed=start_embed)

                        profile = {
                            "username": str.lower(profile_ref["name"]),
                            "userid": profile_ref["id"],
                            "issuer": str.lower(ctx.author.display_name),
                            "reason": reason,
                            "issuedate": datetime.datetime.now(),
                            "duration": length,
                            "ranks": json.dumps(rank),
                            "active": suspension
                        }
                        #send_db(profile,"susdb")
                        susdb.insert_one(profile)

                        if suspension:
                            # remove ranks (pls optimize later)
                            if 32941073 in rank: #main
                                async with httpx.AsyncClient() as client:
                                    await set_rank(profile_ref["id"],32941073,100749843)
                                await client.aclose()
                            if 8294909 in rank: #admin
                                async with httpx.AsyncClient() as client:
                                    await set_rank(profile_ref["id"],8294909,59556661)
                                await client.aclose()
                            if 8294866 in rank: #security
                                async with httpx.AsyncClient() as client:
                                    await set_rank(profile_ref["id"],8294866,105270612)
                                await client.aclose()
                            if 10021698 in rank: #relations
                                async with httpx.AsyncClient() as client:
                                    await set_rank(profile_ref["id"],10021698,59981068)
                                await client.aclose()

                        await button.view.message.edit(embed=start_embed, view=None)
                        self.stop()

                    @discord.ui.button(label="No",emoji="❌")
                    async def no_callback(self, button: discord.ui.Button, ctx2):
                        await button.view.message.delete()
                        self.stop()

                cv = check_view()
                await ctx.respond(embed=check_embed, view=cv)
            else:
                error_embed = discord.Embed(title="An error occured",description="You cannot discipline this member.",color=discord.Color.red())
                await ctx.respond(embed=error_embed, ephemeral=True)

        elif suspension_profile != None:
            error_embed = discord.Embed(title="An error occured",description="This player is currently suspended.",color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
        else:
            error_embed = discord.Embed(title="An error occured",description="This player is not a staff member or cannot be punished.",color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)

    """
    command: unsuspend
    access: mgmt
    input: username/reason
    front end: unsuspends a player and logs reason
    back end: sets active db doc to False, reinstates ranks
    """
    @staffcmd.command(description="Issues a punishment to the staff member.",guild_ids=[1328458609163763804])
    @commands.has_role(1359804131828564028)
    async def unsuspend(self, ctx, username: str, reason: str):
        await ctx.defer()

        profile_ref = None
        try:
            profile_ref = await get_robloxprofile(username)
        except Exception as e:
            error_embed = discord.Embed(title="An error occured",description=e,color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)

        suspension_profile = susdb.find_one({"userid": profile_ref["id"], "active": True})
        if suspension_profile != None:
            embed = discord.Embed(title="Employee Manually Reinstated",color=discord.Color.blurple())
            embed.add_field(name="Employee",value=profile_ref["name"],inline=True)
            embed.add_field(name="Issuer", value=ctx.author.display_name,inline=True)
            embed.add_field(name="Reason",value=reason,inline=False)
            await bot.bot.get_channel(1359454889704427603).send(embed=embed)

            susdb.update_one({"$set": {"active": False}})
            # re-give ranks (pls optimize later)
            rank = json.loads(suspension_profile["ranks"])
            print(rank)
            if 32941073 in rank: #main
                async with httpx.AsyncClient() as client:
                    await set_rank(profile_ref["id"],32941073,rank[32941073]["id"])
                await client.aclose()
            if 8294909 in rank: #admin
                async with httpx.AsyncClient() as client:
                    await set_rank(profile_ref["id"],8294909,rank[8294909]["id"])
                await client.aclose()
            if 8294866 in rank: #security
                async with httpx.AsyncClient() as client:
                    await set_rank(profile_ref["id"],8294866,rank[8294866]["id"])
                await client.aclose()
            if 10021698 in rank: #relations
                async with httpx.AsyncClient() as client:
                    await set_rank(profile_ref["id"],10021698,rank[10021698]["id"])
                await client.aclose()

            await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Staff(bot))