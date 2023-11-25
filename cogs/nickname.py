import discord, db.database as database, Core.utils as utils
import discord, os, asyncio
from discord.ext import commands

class nicknamE(commands.Cog):
    def __init__(self, client):
        self.bot = client  

    @commands.command(
        aliases = ['nickname', 'nickn', 'nic', 'rename', 'setnick'],
        usage = "Manage nicknames",
        description = "Change a specified users nickname in the server",
        brief = "Member, Nickname",
        help = "```Syntax: nickname [member] [nickname]\nExample: nickname @blame best bot```"
    )
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member=None, *, nickname):
        if member == None:
            member == ctx.author
        if member.top_role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
            return await ctx.send("You cannot edit a nickname of someone that is above you.")
        else:
            await member.edit(nick=nickname)
            await ctx.message.add_reaction("✅")





async def setup(client): 
   await client.add_cog(nicknamE(client))