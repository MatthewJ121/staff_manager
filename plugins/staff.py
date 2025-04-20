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

                        # send dm
                        if suspension:
                            message_embed = discord.Embed(
                                title="Notice of Disciplinary Action",
                                description=f"""Hello, {username.display_name},

                                Upon review of your recent behavior, it has become apparent that your performance and conduct have not aligned with the expectations and standards that we have for our team members.  You are receiving this message because of the following infraction(s)

                                - {reason}

                                Regrettably, this has led to the decision to **issue a {length} launch suspension**, effective immediately.

                                You may create an appeal [here](https://discord.com/channels/907125046793879602/1164369435545583647) under Class C Appeals if you believe this action was unjust.

                                Sincerely,
                                {ctx.author.display_name}
                                """,
                                color=discord.Color.dark_red())
                            message_embed.set_footer(text="You will only receive automated messages about Silver Oaks from this bot.\nReport suspcious activity to a Superintendent immediately.")
                            await username.send(embed=message_embed)
                        else:
                            message_embed = discord.Embed(
                                title="Notice of Disciplinary Action",
                                description=f"""Hello, {username.display_name},

                                Upon review of your recent behavior, it has become apparent that your performance and conduct have not aligned with the expectations and standards that we have for our team members.  You are receiving this message because of the following infraction(s)

                                - {reason}

                                You are receiving a **written warning** for this infraction.  This incident has been logged on your record.
                                Further incidents will result in harsher punishments.

                                You may create an appeal [here](https://discord.com/channels/907125046793879602/1164369435545583647) under Class C Appeals if you believe this action was unjust.

                                Sincerely,
                                {ctx.author.display_name}
                                """,
                                color=discord.Color.dark_orange())
                            message_embed.set_footer(text="You will only receive automated messages about Silver Oaks from this bot.\nReport suspcious activity to a Superintendent immediately.")
                            await username.send(embed=message_embed)

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
    @staffcmd.command(description="Manually unsuspends a suspended member.",guild_ids=[1328458609163763804])
    @commands.has_role(1359804131828564028)
    async def unsuspend(self, ctx, username: discord.Option(str, description="The roblox username of the target user."), reason: str):
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

            susdb.update_one(suspension_profile,{"$set": {"active": False}})
            # re-give ranks (pls optimize later)
            rank = json.loads(suspension_profile["ranks"])
            print(rank)
            if '32941073' in rank: #main
                async with httpx.AsyncClient() as client:
                    await set_rank(profile_ref["id"],32941073,rank['32941073']["id"])
                await client.aclose()
            if '8294909' in rank: #admin
                async with httpx.AsyncClient() as client:
                    await set_rank(profile_ref["id"],8294909,rank['8294909']["id"])
                await client.aclose()
            if '8294866' in rank: #security
                async with httpx.AsyncClient() as client:
                    await set_rank(profile_ref["id"],8294866,rank['8294866']["id"])
                await client.aclose()
            if '10021698' in rank: #relations
                async with httpx.AsyncClient() as client:
                    await set_rank(profile_ref["id"],10021698,rank['10021698']["id"])
                await client.aclose()

            await ctx.respond(embed=embed)

    """
    command: unsuspend
    access: mgmt
    input: username/reason
    front end: unsuspends a player and logs reason
    back end: sets active db doc to False, reinstates ranks
    """
    @staffcmd.command(description="Manually adds launches to a user's record.  The value can be negative.",guild_ids=[1328458609163763804])
    @commands.has_role(1359804131828564028)
    @discord.option("username",description="The roblox username of the target employee.")
    @discord.option("amount",description="The amount of launches to add.  The value can be negative to remove launches.")
    @discord.option("reason",description="Reason for launch adjustment.")
    async def adjustlaunches(self, ctx, username: str, amount: int, reason: str):
        profile_ref = None
        try: # pull uid
            profile_ref = await get_robloxprofile(username)
        except Exception as e:
            error_embed = discord.Embed(title="An error occured",description=e,color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
        
        s_profile = sdb.find_one({"userid":profile_ref["id"]})
        print(s_profile)
        if s_profile != None: # handle database file
            try:
                s_profile = sdb.find_one({"userid":profile_ref["id"]})
                sdb.update_one(s_profile,{"$set": {"launches": s_profile["launches"]+amount}})
            except Exception as e:
                error_embed = discord.Embed(title="An error occured",description=e,color=discord.Color.red())
                await ctx.respond(embed=error_embed, ephemeral=True)
            
            success_embed = discord.Embed(description="✅ Launches adjusted successfully",color=discord.Color.dark_blue())

            log_embed = discord.Embed(title="Launch Record Adjusted",color=discord.Color.dark_blue())
            log_embed.add_field(name="Employee",value=profile_ref["name"],inline=True)
            log_embed.add_field(name="Adjuster", value=ctx.author.display_name,inline=True)
            log_embed.add_field(name="Reason",value=reason,inline=False)
            log_embed.add_field(name="Amount",value=f"{amount} launches")

            await bot.bot.get_channel(1362703685372739656).send(embed=log_embed)
            await ctx.respond(embed=success_embed)
        else: # handle no database file
            fail_embed = discord.Embed(description="❌ Couldn't find user in database.",color=discord.Color.dark_red())
            await ctx.respond(embed=fail_embed)
            
        

def setup(bot):
    bot.add_cog(Staff(bot))