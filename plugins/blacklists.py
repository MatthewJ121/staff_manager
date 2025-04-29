import os
import discord
import datetime
import time
import bot
from discord.ext import commands
from plugins.globalfx import *
roblox_api = os.getenv('roblox_api')

class Blacklists(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    factioncmd = discord.SlashCommandGroup("faction")
    """
    command: blacklist
    access: all users
    input: username/code/bltype
    front end: responds with blacklist information and logs blacklist in channel
    back end: writes to bdb, ranks user to visitor
    """
    @commands.slash_command()
    @commands.has_role(director_role) # director
    @discord.option("username",description="The roblox username of the target player.")
    @discord.option("code",description="The codes associated with the violation(s) made.")
    @discord.option("bltype",description="The type of blacklist to issue.",choices=["Class A","Class B","Class C"])
    async def blacklist(self, ctx, username: str, code: str, bltype: str):
        if bltype == "Class B" and not any(role.id == supe_role for role in ctx.author.roles): # handle no supe rank
            error_embed = discord.Embed(title="An error occured",description="You cannot issue Class B blacklists.",color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
        await ctx.defer()

        profile_ref = None
        try:
            profile_ref = await get_robloxprofile(username)
        except Exception as e:
            error_embed = discord.Embed(title="An error occured",description=e,color=discord.Color.red())
            await ctx.send_response(embed=error_embed, ephemeral=True)

        active_bl = bdb.find_one({"ouid":int(profile_ref["id"]),"active":True})
        if active_bl == None:

            async with httpx.AsyncClient() as client:
                picture = await get_picture(profile_ref["id"])
            await client.aclose()

            bl_profile = {
                "offender":str.lower(username),
                "issuer":ctx.author.display_name,
                "code":code,
                "date": datetime.datetime.now(),
                "type":bltype,
                "active":True,
                "ouid": int(profile_ref["id"])
            }
            bdb.insert_one(bl_profile)

            async with httpx.AsyncClient() as client:
                await set_rank(profile_ref["id"],32941073,100662193)
            await client.aclose()

            #log it
            log_embed = discord.Embed(title=f"{bltype} Blacklist Issued",color=discord.Color.dark_red())
            log_embed.set_thumbnail(url=picture)
            log_embed.add_field(name="Violator",value=profile_ref["name"],inline=True)
            log_embed.add_field(name="Issuer", value=ctx.author.display_name,inline=True)
            log_embed.add_field(name="Reason",value=code,inline=False)
            await bot.bot.get_channel(1366698195488477215).send(embed=log_embed)

            await ctx.respond(embed=log_embed,ephemeral=True)
        else:
            error_embed = discord.Embed(title="An error occured",description="This user is already blacklisted.",color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
    
    """
    command: unblacklist
    access: RC, FS+
    input: username/code/bltype
    front end: responds with blacklist information and logs unblacklist in channel
    back end: what do you think happens
    """
    @commands.slash_command()
    @commands.has_any_role(director_role,supervisor_role) # director, supervisor
    @discord.option("username",description="The roblox username of the target player.")
    @discord.option("reason",description="The reason for the blacklist removal.")
    async def unblacklist(self, ctx, username: str, reason: str):
        await ctx.defer()
        profile_ref = None
        try:
            profile_ref = await get_robloxprofile(username)
        except Exception as e:
            error_embed = discord.Embed(title="An error occured",description=e,color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)

        active_bl = bdb.find_one({"ouid":int(profile_ref["id"]),"active":True})
        if active_bl != None:
            async with httpx.AsyncClient() as client:
                picture = await get_picture(profile_ref["id"])
            await client.aclose()
            # handle no supe rank
            if active_bl["type"] == "Class B" and not any(role.id == supe_role for role in ctx.author.roles): 
                error_embed = discord.Embed(title="An error occured",description="You cannot remove Class B blacklists.",color=discord.Color.red())
                await ctx.respond(embed=error_embed, ephemeral=True)
            # handle no director rank
            if active_bl["type"] == "Class C" and not any(role.id == director_role for role in ctx.author.roles): 
                error_embed = discord.Embed(title="An error occured",description="You cannot remove Class C blacklists.",color=discord.Color.red())
                await ctx.respond(embed=error_embed, ephemeral=True)
            
            if active_bl["type"] == "Class A" or (active_bl["type"] == "Class B" and any(role.id == supe_role for role in ctx.author.roles)) or (active_bl["type"] == "Class C" and any(role.id == director_role for role in ctx.author.roles)):
                
                bdb.find_one_and_update({"ouid": int(profile_ref["id"]), "active": True}, {"$set": {"active": False}})

                #log it
                bltype = active_bl["type"]
                log_embed = discord.Embed(title=f"{bltype} Blacklist Rescinded",color=discord.Color.dark_green())
                log_embed.set_thumbnail(url=picture)
                log_embed.add_field(name="Violator",value=profile_ref["name"],inline=True)
                log_embed.add_field(name="Issuer", value=active_bl["issuer"],inline=True)
                log_embed.add_field(name="Codes Violated",value=active_bl["code"],inline=False)
                log_embed.add_field(name="Remover",value=ctx.author.display_name, inline = False)
                log_embed.add_field(name="Removal Reason",value=reason,inline=True)
                await bot.bot.get_channel(1366698195488477215).send(embed=log_embed)

                await ctx.respond(embed=log_embed)

    """
    command: faction blacklist
    access: superintendents
    input: username/code/bltype
    front end: responds with blacklist information and logs blacklist in channel
    back end: writes to bdb
    """
    @factioncmd.command()
    @commands.has_role(supe_role) # director
    @discord.option("groupid",description="The group ID of the organization to blacklist.")
    @discord.option("code",description="The codes associated with the violation(s) made.")
    async def blacklist(self, ctx, groupid: str, code: str):
        await ctx.defer()

        group = None
        try:
            group = httpx.get(f"https://apis.roblox.com/cloud/v2/groups/{groupid}",headers={"x-api-key":(egg_key)}).json()
        except Exception as e:
            error_embed = discord.Embed(title="An error occured",description=e,color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
        print(group["displayName"])

        if group != None:
            active_bl = gbdb.find_one({"ouid":groupid})
            if active_bl == None:
                bl_profile = {
                    "groupid":int(groupid),
                    "issuer":ctx.author.display_name,
                    "reason":code,
                    "date": datetime.datetime.now(),
                }
                gbdb.insert_one(bl_profile)

                #log it
                log_embed = discord.Embed(title="Faction Blacklist Issued",color=discord.Color.red())
                log_embed.add_field(name="Faction Name",value=group["displayName"],inline=False)
                log_embed.add_field(name="Issuer", value=ctx.author.display_name,inline=False)
                log_embed.add_field(name="Reason",value=code,inline=False)
                await bot.bot.get_channel(1366698195488477215).send(embed=log_embed)

                #announce it
                g_name = group["displayName"]
                announce_embed = discord.Embed(title="<:silveroaks:1173424385835675689> | Office of the Superintendent",color=discord.Color.dark_red())
                announce_embed.description = f"`{g_name}` (and related divisions and organizations) have been added to the Hostile Organization list.  You have 24 hours to leave that organization or face a blacklist under criminal code § II-B-3.\n\n{ctx.author.display_name}\n{ctx.author.top_role.name}"
                await bot.bot.get_channel(1366728082584633344).send(embed=announce_embed)

                await ctx.respond(embed=log_embed,ephemeral=True)
            else:
                error_embed = discord.Embed(title="An error occured",description="This faction is already blacklisted.",color=discord.Color.red())
                await ctx.respond(embed=error_embed, ephemeral=True)
    
    """
    command: unblacklist
    access: RC, FS+
    input: username/code/bltype
    front end: responds with blacklist information and logs unblacklist in channel
    back end: what do you think happens
    """
    '''
    @commands.slash_command()
    @commands.has_any_role(director_role,supervisor_role) # director, supervisor
    @discord.option("username",description="The roblox username of the target player.")
    @discord.option("reason",description="The reason for the blacklist removal.")
    async def unblacklist(self, ctx, username: str, reason: str):
        await ctx.defer()
        group = None
        try:
            group = httpx.get(httpx.get(f"https://apis.roblox.com/cloud/v2/groups/{groupid}/",headers={"x-api-key":(egg_key)})).json()
        except Exception as e:
            error_embed = discord.Embed(title="An error occured",description="No group found.",color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)

        if group != None:
            active_bl = bdb.find_one({"ouid":int(profile_ref["id"]),"active":True})
            if active_bl != None:
                async with httpx.AsyncClient() as client:
                    picture = await get_picture(profile_ref["id"])
                await client.aclose()
                # handle no supe rank
                if active_bl["type"] == "Class B" and not any(role.id == supe_role for role in ctx.author.roles): 
                    error_embed = discord.Embed(title="An error occured",description="You cannot remove Class B blacklists.",color=discord.Color.red())
                    await ctx.respond(embed=error_embed, ephemeral=True)
                # handle no director rank
                if active_bl["type"] == "Class C" and not any(role.id == director_role for role in ctx.author.roles): 
                    error_embed = discord.Embed(title="An error occured",description="You cannot remove Class C blacklists.",color=discord.Color.red())
                    await ctx.respond(embed=error_embed, ephemeral=True)
                
                if active_bl["type"] == "Class A" or (active_bl["type"] == "Class B" and any(role.id == supe_role for role in ctx.author.roles)) or (active_bl["type"] == "Class C" and any(role.id == director_role for role in ctx.author.roles)):
                    
                    bdb.find_one_and_update({"ouid": int(profile_ref["id"]), "active": True}, {"$set": {"active": False}})

                    #log it
                    bltype = active_bl["type"]
                    log_embed = discord.Embed(title=f"{bltype} Blacklist Rescinded",color=discord.Color.dark_green())
                    log_embed.set_thumbnail(url=picture)
                    log_embed.add_field(name="Violator",value=profile_ref["name"],inline=True)
                    log_embed.add_field(name="Issuer", value=active_bl["issuer"],inline=True)
                    log_embed.add_field(name="Codes Violated",value=active_bl["code"],inline=False)
                    log_embed.add_field(name="Remover",value=ctx.author.display_name, inline = False)
                    log_embed.add_field(name="Removal Reason",value=reason,inline=True)
                    await bot.bot.get_channel(1366698195488477215).send(embed=log_embed)

                    await ctx.respond(embed=log_embed)
'''

def setup(bot):
    bot.add_cog(Blacklists(bot))