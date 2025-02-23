import os
import discord
from discord.ext import commands
from plugins.globalfx import *
roblox_api = os.getenv('roblox_api')

class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    staffcmd = discord.SlashCommandGroup("mgmt")
    """
    command: viewprofile
    access: all users
    input: username/id
    front end: displays embed with basic user info, blacklist status, alt flags, and launches
    back end: pulls information from roblox api and mongodb databases for relevant information, read only
    """
    @staffcmd.command(guild_ids=[1328458609163763804])
    async def suspend(self, ctx, username: str, reason: str, length: int):
        
        profile_ref = None
        try:
            profile_ref = await get_robloxprofile(username)
        except Exception as e:
            error_embed = discord.Embed(title="An error occured",description=e,color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)

        suspension_profile = susdb.find_one({"ouid": profile_ref["id"], "active": True})
        if suspension_profile == None:
            picture = None
            try:
                picture = await get_picture(profile_ref["id"])
            except Exception as e:
                print(e)

            check_embed = discord.Embed(title="Is this the right person?",color=discord.Color.blurple())
            check_embed.set_thumbnail(url=picture)
            check_embed.add_field(name="Username",value=profile_ref["name"])
            check_embed.add_field(name="Reason",value=reason)
            check_embed.add_field(name="Length",value=length)

            class check_view(discord.ui.View):
                def __init__(self):
                    super().__init__()
                    self.value = None

                @discord.ui.button(label="Yes",emoji="✅")
                async def yes_callback(self, button: discord.ui.Button, ctx2):
                    await button.view.message.edit("test",embed=None, view=None)
                    self.stop()

                @discord.ui.button(label="No",emoji="❌")
                async def no_callback(self, button: discord.ui.Button, ctx2):
                    await button.view.message.delete()
                    self.stop()

            cv = check_view()
            await ctx.respond(embed=check_embed, view=cv)

            
            new_profile = {
                "ouid": profile_ref["id"],
                "active": True,
                "reason": reason,
                "length": length
            }
        else:
            error_embed = discord.Embed(title="An error occured",description="This player is already suspended.",color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
        

def setup(bot):
    bot.add_cog(Staff(bot))