import discord,difflib, humanize, Core.confirm as cop_is_gae, aiohttp
from discord.ext import commands

from Core import confirm
from Core import utils as util
import typing, humanfriendly, motor.motor_asyncio
import datetime
import tweepy
import random, re, asyncio
from discord import ui
from datetime import timedelta
from discord.ext.commands import errors
from bs4 import BeautifulSoup
import time, math
from typing import Union
from Core.utils import get_theme


class mod(commands.Cog):
    def __init__(self, client):
        self.bot = client
        self.add="<:plus:1016070171326165012>"
        self.yes="<:check:921544057312915498>"
        self.rem="<:rem:947812531509026916>"
        self.no="<:yy_yno:921559254677200957>"
        self.bad=0xA90F25
        self.restore = {}
        self.snipe_limit=3
        self.userdb = self.bot.db["userJail"]
        self.guilddb = self.bot.db["guildJail"]
        self.aliases = self.bot.db["aliases"]
        self.bans = self.bot.db['bans']
        self.guildTasks = []

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        roles=[]
        if not member.bot:
            if member.id not in self.restore:
                self.restore[member.id] = []
            member_roles = [role for role in member.roles if role.name != '@everyone']
            for role in member_roles:
                roles.append(f"{role.id}")
            new_lst=(','.join(str(a)for a in roles))
            newroles=f"{new_lst}"
            self.restore[member.id].append(newroles)
            try:
                if len(self.restore[member.id]) > self.snipe_limit:
                    self.restore[member.id].pop(0)
            except:
                pass

    @commands.group(
        invoke_without_command=True,
        description="give or take a role from a member",
        usage="manage_roles",
        brief="member, role",
        help="```Example: ;role @cop#0001 users```")
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx, member: discord.Member=None, *, role: typing.Union[ discord.Role, str]=None):
        try:
            if isinstance(role, discord.Role):
                r=role
                if r.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                    return await ctx.send(embed=discord.Embed(description=f"{r.mention} is higher then your top role {ctx.author.mention}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                if r.position >= ctx.guild.me.top_role.position:
                    return await ctx.send(embed=discord.Embed(description=f"{r.mention} is higher then my top role therefore i cant give it", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                if ctx.author.id == ctx.guild.owner.id:
                    pass
                if not role.is_assignable():
                    return await ctx.reply(embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f" {ctx.author.mention}: **i cannot give a managed role**"))
                if r in member.roles:
                    await member.remove_roles(r)
                    embed = discord.Embed(description=f"{self.rem}{ctx.author.mention}: Removed {r.mention} from {member.mention}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                    return  await ctx.send(embed=embed)
                else:
                    await member.add_roles(r)
                    embed = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"{self.add}{ctx.author.mention}: Added {r.mention} to {member.mention}")
                    return await ctx.send(embed=embed)
            if isinstance(role, str):
                r=role.lower()
                roles=[role.name.lower() for role in ctx.guild.roles if role.is_assignable() and r in role.name.lower()]
                closest=difflib.get_close_matches(role.lower(), roles,n=1, cutoff=0)
                if closest:
                    for role in ctx.guild.roles:
                        if role.name.lower() == closest[0].lower():
                            rr=role
                    if rr.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                        return await ctx.send(embed=discord.Embed(description=f"{rr.mention} is higher then your top role {ctx.author.mention}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                    if rr.position >= ctx.guild.me.top_role.position:
                        return await ctx.send(embed=discord.Embed(description=f"{rr.name} is higher then my top role therefore i cant give it", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                    if ctx.author.id == ctx.guild.owner.id:
                        pass
                    if rr in member.roles:
                        await member.remove_roles(rr)
                        embed = discord.Embed(description=f"{self.rem}{ctx.author.mention}: Removed  {rr.mention} from {member.mention}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                        return await ctx.send(embed=embed)
                    else:
                        await member.add_roles(rr)
                        embed = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"{self.add}{ctx.author.mention}: Added {rr.mention} to {member.mention}")
                        return await ctx.send(embed=embed)
            if member or role is None:
               return await util.command_help(ctx)
            else:
                return await util.send_issue(ctx, f"I could not find the role {role}")
        except:
            pass
            embed = discord.Embed(title="Group Command: role", description="Do anything revolving around edit/create/deleting a role\n```Syntax: role [subcommand] <arg>\nExample: role create hii```", color = discord.Color.blurple())
            embed.set_author(name="role help", icon_url=ctx.me.avatar.url)
            embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('role').walk_commands()])} ・ role")
            return await ctx.send(embed=embed)

    @role.command(
        aliases = ['cr'],
        usage = 'manage_roles',
        description='Create a role in your server',
        brief= 'role_name',
        help = '```Syntax: role create [role_name]\nExample: role create blame is awesome```'
    )
    @commands.has_permissions(manage_roles=True)
    async def create(self, ctx, *, name):
        await util.send_blurple(ctx, f"Created the role ``{name}``")
        return await ctx.guild.create_role(name=name)

    @role.command(
        aliases = ['del'],
        usage = 'manage_roles',
        description = 'Delete a role in your server',
        brief = 'role_name',
        help = '```Syntax: role delete [role_name]\nExample: role delete blame is awesome```'
    )
    async def delete(self, ctx, *, role: typing.Union[ discord.Role, str]):
        if isinstance(role, discord.Role):
            r=role
            if r.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                return await util.send_issue(ctx, f"You cannot delete a role that is higher than your top role!")
            if r.position >= ctx.guild.me.top_role.position:
                return await util.send_issue(ctx, f"I don't have access to that role since it is higher than me!")
            if ctx.author.id == ctx.guild.owner.id:
                pass
            if not role.is_assignable():
                return await util.send_error(ctx, f"I can't delete a ``managed`` role.")
            else:
                await r.delete(reason=f'Deleted by {ctx.author}')
                return await util.send_blurple(ctx, f"Deleted the role: ``{role}``")
        if isinstance(role, str):
            r=role.lower()
            roles=[role.name.lower() for role in ctx.guild.roles if role.is_assignable() and r in role.name.lower()]
            closest=difflib.get_close_matches(role.lower(), roles,n=1, cutoff=0)
            if closest:
                for role in ctx.guild.roles:
                    if role.name.lower() == closest[0].lower():
                        rr=role
                if rr.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                    return await util.send_issue(ctx, f"You cannot delete a role that is higher than your top role!")
                if rr.position >= ctx.guild.me.top_role.position:
                    return await util.send_issue(ctx, f"I don't have access to that role since it is higher than me!")
                if ctx.author.id == ctx.guild.owner.id:
                    pass
                if not role.is_assignable():
                    return await util.send_error(ctx, f"I can't delete a ``managed`` role.")
                else:
                    await rr.delete(reason=f'Deleted by {ctx.author}')
                    return await util.send_blurple(ctx, f"Deleted the role: ``{role}``")
        else:
            return await util.send_issue(ctx, f"I could not find the role: ``{role}``")

    @role.command(
        aliases = ['hois', 'hoisted'],
        usage = 'manage_roles',
        description = 'Hoist a specified role',
        brief = 'role_name',
        help = '```Syntax: role hoist [role_name]\nExample: role hoist owners```'
    )
    @commands.has_permissions(manage_roles=True)
    async def hoist(self, ctx, *, role: typing.Union[ discord.Role, str]):
        if isinstance(role, discord.Role):
            r=role
            if r.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                return await util.send_issue(ctx, f"You cannot edit a role that is higher than your top role!")
            if r.position >= ctx.guild.me.top_role.position:
                return await util.send_issue(ctx, f"I don't have access to that role since it is higher than me!")
            if ctx.author.id == ctx.guild.owner.id:
                pass
            if not role.is_assignable():
                return await util.send_error(ctx, f"I can't hoist a ``managed`` role.")
            else:
                if r.hoist is True:
                    await r.edit(hoist=False, reason=f'Set to unhoisted by {ctx.author}')
                    return await util.send_blurple(ctx, f"Unhoisted the role: ``{role}``")
                else:
                    await r.edit(hoist=True, reason=f'Set to hoisted by {ctx.author}')
                    return await util.send_blurple(ctx, f"Hoisted the role: ``{role}``") 
        if isinstance(role, str):
            r=role.lower()
            roles=[role.name.lower() for role in ctx.guild.roles if role.is_assignable() and r in role.name.lower()]
            closest=difflib.get_close_matches(role.lower(), roles,n=1, cutoff=0)
            if closest:
                for role in ctx.guild.roles:
                    if role.name.lower() == closest[0].lower():
                        rr=role
                if rr.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                    return await util.send_issue(ctx, f"You cannot edit a role that is higher than your top role!")
                if rr.position >= ctx.guild.me.top_role.position:
                    return await util.send_issue(ctx, f"I don't have access to that role since it is higher than me!")
                if ctx.author.id == ctx.guild.owner.id:
                    pass
                if not role.is_assignable():
                    return await util.send_error(ctx, f"I can't hoist a ``managed`` role.")
                else:
                    if rr.hoist is True:
                        await rr.edit(hoist=False, reason=f'Set to unhoisted by {ctx.author}')
                        return await util.send_blurple(ctx, f"Unhoisted the role: ``{role}``")
                    else:
                        await rr.edit(hoist=True, reason=f'Set to hoisted by {ctx.author}')
                        return await util.send_blurple(ctx, f"Hoisted the role: ``{role}``")         
        else:
            return await util.send_issue(ctx, f"I could not find the role: ``{role}``")

    @role.command(
        aliases = ['colour'],
        usage = 'manage_roles',
        description = 'Change the color of a role',
        brief = 'role_name, color',
        help = '```Syntax: role color [role_name] [color]\nExample: role color Users #f7f7f7```'
    )
    @commands.has_permissions(manage_roles=True)
    async def color(self, ctx, role: typing.Union[ discord.Role, str], color: typing.Union[int, str]):
        if isinstance(role, discord.Role):
            r=role
            if r.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                return await util.send_issue(ctx, f"You cannot edit a role that is higher than your top role!")
            if r.position >= ctx.guild.me.top_role.position:
                return await util.send_issue(ctx, f"I don't have access to that role since it is higher than me!")
            if ctx.author.id == ctx.guild.owner.id:
                pass
            if not role.is_assignable():
                return await util.send_error(ctx, f"I can't hoist a ``managed`` role.")
            else:
                if '#' in color:
                    match = re.search(r'^#(?:[0-9a-fA-F]{1,2}){3}$', color)
                    if match:
                        color = color.strip('#')
                        await r.edit(color=int(color))
                        return await util.send_blurple(ctx, f"Changed the role: ``{role}'s`` color to: ``{color}``")
                    else:
                        return await util.send_error(ctx, f"The color: ``{color}`` is not supported.")
                if not '#' in color:
                    color = color.replace(color, f'#{color}')
                    match = re.search(r'^#(?:[0-9a-fA-F]{1,2}){3}$', color)
                    if match:
                        color = color.strip('#')
                        await r.edit(color=int(color, 16))
                        return await util.send_blurple(ctx, f"Changed the role: ``{role}'s`` color to: ``{color}``")
                    else:
                        return await util.send_error(ctx, f"The color: ``{color}`` is not supported.")

        if isinstance(role, str):
            r=role.lower()
            roles=[role.name.lower() for role in ctx.guild.roles if role.is_assignable() and r in role.name.lower()]
            closest=difflib.get_close_matches(role.lower(), roles,n=1, cutoff=0)
            if closest:
                for role in ctx.guild.roles:
                    if role.name.lower() == closest[0].lower():
                        rr=role
                if rr.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                    return await util.send_issue(ctx, f"You cannot edit a role that is higher than your top role!")
                if rr.position >= ctx.guild.me.top_role.position:
                    return await util.send_issue(ctx, f"I don't have access to that role since it is higher than me!")
                if ctx.author.id == ctx.guild.owner.id:
                    pass
                if not role.is_assignable():
                    return await util.send_error(ctx, f"I can't hoist a ``managed`` role.")
                else:
                    if '#' in color:
                        match = re.search(r'^#(?:[0-9a-fA-F]{1,2}){3}$', color)
                        if match:
                            color = color.strip('#')
                            await rr.edit(color=int(color))
                            return await util.send_blurple(ctx, f"Changed the role: ``{role}'s`` color to: ``{color}``")
                        else:
                            return await util.send_error(ctx, f"The color: ``{color}`` is not supported.")
                    if not '#' in color:
                        color = color.replace(color, f'#{color}')
                        match = re.search(r'^#(?:[0-9a-fA-F]{1,2}){3}$', color)
                        if match:
                            color = color.strip('#')
                            await rr.edit(color=int(color, 16))
                            return await util.send_blurple(ctx, f"Changed the role: ``{role}'s`` color to: ``{color}``")
                        else:
                            return await util.send_error(ctx, f"The color: ``{color}`` is not supported.")       
        else:
            return await util.send_issue(ctx, f"I could not find the role: ``{role}``")

    @role.command(
        aliases = ['everyone'],
        usage = 'manage_roles',
        description = 'Role all members in your server with a specified role',
        brief = 'role_name',
        help = '```Syntax: role all [role_name]\nExample: role all Members```'
    )
    @commands.has_permissions(manage_roles=True)
    async def all(self, ctx, *, role: typing.Union[ discord.Role, str]):
        if isinstance(role, discord.Role):
            r=role
            if r.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                return await util.send_issue(ctx, f"You cannot give a role that is higher than your top role!")
            if r.position >= ctx.guild.me.top_role.position:
                return await util.send_issue(ctx, f"I don't have access to that role since it is higher than me!")
            if ctx.author.id == ctx.guild.owner.id:
                pass
            if not role.is_assignable():
                return await util.send_error(ctx, f"I can't give a ``managed`` role.")
            else:
                time = datetime.timedelta(seconds=len([i for i in ctx.guild.members if not r in i.roles]))
                totalTime = humanize.naturaldelta(time)
                await util.send_blurple(ctx, f"Attempting to role ``{len([i for i in ctx.guild.members if not r in i.roles])} members`` with the role: {role.mention}. This will take approximatley: {totalTime}")
                count = 0
                for i in ctx.guild.members:
                    if not r in i.roles:
                        try:
                            await i.add_roles(r)
                            count +=1
                        except:
                            pass
                return await ctx.reply(embed=discord.Embed(description=f"Completed giving the role: {r.mention} to: ``{count}`` members in: {totalTime}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
        if isinstance(role, str):
            r=role.lower()
            roles=[role.name.lower() for role in ctx.guild.roles if role.is_assignable() and r in role.name.lower()]
            closest=difflib.get_close_matches(role.lower(), roles,n=1, cutoff=0)
            if closest:
                for role in ctx.guild.roles:
                    if role.name.lower() == closest[0].lower():
                        rr=role
                if rr.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                    return await util.send_issue(ctx, f"You cannot edit a role that is higher than your top role!")
                if rr.position >= ctx.guild.me.top_role.position:
                    return await util.send_issue(ctx, f"I don't have access to that role since it is higher than me!")
                if ctx.author.id == ctx.guild.owner.id:
                    pass
                if not role.is_assignable():
                    return await util.send_error(ctx, f"I can't give a ``managed`` role.")
                else:
                    time = datetime.timedelta(seconds=len([i for i in ctx.guild.members if not rr in i.roles]))
                    totalTime = humanize.naturaldelta(time)
                    await util.send_blurple(ctx, f"Attempting to role ``{len([i for i in ctx.guild.members if not rr in i.roles])} members`` with the role: {role.mention}. This will take approximatley: **{totalTime}**")
                    count = 0
                    for i in ctx.guild.members:
                        if not rr in i.roles:
                            try:
                                await i.add_roles(rr)
                                count +=1
                            except:
                                pass
                    return await ctx.reply(embed=discord.Embed(description=f"<:check:1027703035054526475> Completed giving the role: {rr.mention} to: ``{count} members`` in: **{totalTime}**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))       
        else:
            return await util.send_issue(ctx, f"I could not find the role: ``{role}``")
    
    @role.command(
        aliases = ['pfp', 'image'],
        usage = 'manage_roles',
        description = 'Change the icon of a specified role',
        brief = 'role, url',
        help = '```Syntax: role icon [role] [url]\nExample: role icon https://image.jpg```'
    )
    async def icon(self, ctx, role: discord.Role, url: str=None):
        try:
            if not ctx.guild.premium_tier == 3:
                return await util.send_issue(ctx, 'This guild does not reach the required boost level.')
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            if url is discord.Emoji:
                url = url.url
            if url.startswith('<:'):
                emoji = re.findall('<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>', url)
                a = [x[2] for x in emoji]
                await ctx.send(a)
                get = self.bot.get_emoji(int(a[0]))
                url = get.url
            if role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                return await util.send_issue(ctx, f"You cannot edit a role that is higher than your top role!")
            if role.position >= ctx.guild.me.top_role.position:
                return await util.send_issue(ctx, f"I don't have access to that role since it is higher than me!")
            if ctx.author.id == ctx.guild.owner.id:
                pass
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    await role.edit(display_icon= await response.read(), reason=f"Changed by: {ctx.author}")
        except Exception as e:
            print(e); return await util.send_issue(ctx, f"Invalid icon. ``Please try {ctx.prefix}help role icon``")

    @role.group(
        invoke_without_command=True,
        usage = 'manage_roles',
        description = 'Give a role to all humans in your server',
        brief = 'role_name',
        help = '```Syntax: role humans [role_name]\nExample: role humans Members```'
    )
    @commands.has_permissions(manage_roles=True)
    async def humans(self, ctx, *, role: typing.Union[ discord.Role, str]=None):
        if isinstance(role, discord.Role):
            r=role
            if r.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                return await util.send_issue(ctx, f"You cannot give a role that is higher than your top role!")
            if r.position >= ctx.guild.me.top_role.position:
                return await util.send_issue(ctx, f"I don't have access to that role since it is higher than me!")
            if ctx.author.id == ctx.guild.owner.id:
                pass
            if not role.is_assignable():
                return await util.send_error(ctx, f"I can't give a ``managed`` role.")
            else:
                if ctx.guild.id in self.guildTasks:
                    return await util.send_issue(ctx, f'A ``role humans`` is already in progress!')
                else:
                    self.guildTasks.append(ctx.guild.id)
                    time = datetime.timedelta(seconds=len([i for i in ctx.guild.members if not i.bot and not r in i.roles]))
                    totalTime = humanize.naturaldelta(time)
                    await util.send_blurple(ctx, f"Attempting to role ``{len([i for i in ctx.guild.members if not i.bot and not r in i.roles])} humans`` with the role: {role.mention}. This will take approximatley: {totalTime}")
                    count = 0
                    for i in ctx.guild.members:
                        if not i.bot and not r in i.roles:
                            try:
                                await i.add_roles(r)
                                count +=1
                            except:
                                pass
                    self.guildTasks.remove(ctx.guild.id)
                    return await ctx.reply(embed=discord.Embed(description=f"Completed giving the role: {r.mention} to: ``{count}`` humans in: {totalTime}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
        if isinstance(role, str):
            r=role.lower()
            roles=[role.name.lower() for role in ctx.guild.roles if role.is_assignable() and r in role.name.lower()]
            closest=difflib.get_close_matches(role.lower(), roles,n=1, cutoff=0)
            if closest:
                for role in ctx.guild.roles:
                    if role.name.lower() == closest[0].lower():
                        rr=role
                if rr.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                    return await util.send_issue(ctx, f"You cannot edit a role that is higher than your top role!")
                if rr.position >= ctx.guild.me.top_role.position:
                    return await util.send_issue(ctx, f"I don't have access to that role since it is higher than me!")
                if ctx.author.id == ctx.guild.owner.id:
                    pass
                if not role.is_assignable():
                    return await util.send_error(ctx, f"I can't give a ``managed`` role.")
                else:
                    if ctx.guild.id in self.guildTasks:
                        return await util.send_issue(ctx, f'A ``role humans`` is already in progress!')
                    else:
                        self.guildTasks.append(ctx.guild.id)
                        time = datetime.timedelta(seconds=len([i for i in ctx.guild.members if not i.bot and not rr in i.roles]))
                        totalTime = humanize.naturaldelta(time)
                        await util.send_blurple(ctx, f"Attempting to role ``{len([i for i in ctx.guild.members if not i.bot and not rr in i.roles])} humans`` with the role: {role.mention}. This will take approximatley: **{totalTime}**")
                        count=0
                        for i in ctx.guild.members:
                            if not i.bot and not rr in i.roles:
                                try:
                                    await i.add_roles(rr)
                                    count+=1
                                except:
                                    pass
                        self.guildTasks.remove(ctx.guild.id)
                        return await ctx.reply(embed=discord.Embed(description=f"Completed giving the role: {rr.mention} to: ``{count} humans`` in: **{totalTime}**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))       
        if role is None:
            embed = discord.Embed(title="Group Command: role humans", description="Give a role to all humans in your server\n```Syntax: role humans [role_name]\nExample: role humans Members```", color = discord.Color.blurple())
            embed.set_author(name="role humans help", icon_url=ctx.me.avatar.url)
            embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('role').walk_commands()])} ・ role humans")
            return await ctx.send(embed=embed)
        else:
            return await util.send_issue(ctx, f"I could not find the role: ``{role}``")

    @role.group(
        usage = 'manage_roles',
        description = 'Give a role to all bots in your server',
        brief = 'role_name',
        help = '```Syntax: role bots [role_name]\nExample: role bots bot_role```'
    )
    @commands.has_permissions(manage_roles=True)
    async def bots(self, ctx, *, role: typing.Union[ discord.Role, str]=None):
        if isinstance(role, discord.Role):
            r=role
            if r.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                return await util.send_issue(ctx, f"You cannot give a role that is higher than your top role!")
            if r.position >= ctx.guild.me.top_role.position:
                return await util.send_issue(ctx, f"I don't have access to that role since it is higher than me!")
            if ctx.author.id == ctx.guild.owner.id:
                pass
            if not role.is_assignable():
                return await util.send_error(ctx, f"I can't give a ``managed`` role.")
            else:
                if ctx.guild.id in self.guildTasks:
                    return await util.send_issue(ctx, f'A ``role bots`` is already in progress!')
                else:
                    self.guildTasks.append(ctx.guild.id)
                    time = datetime.timedelta(seconds=len([i for i in ctx.guild.members if i.bot and not r in i.roles]))
                    totalTime = humanize.naturaldelta(time)
                    await util.send_blurple(ctx, f"Attempting to role ``{len([i for i in ctx.guild.members if i.bot and not r in i.roles])} bots`` with the role: {role.mention}. This will take approximatley: {totalTime}")
                    count = 0
                    for i in ctx.guild.members:
                        if i.bot and not r in i.roles:
                            try:
                                await i.add_roles(r)
                                count +=1
                            except:
                                pass
                    self.guildTasks.remove(ctx.guild.id)
                    return await ctx.reply(embed=discord.Embed(description=f"Completed giving the role: {r.mention} to: ``{count} bots`` in: **{totalTime}**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
        if isinstance(role, str):
            r=role.lower()
            roles=[role.name.lower() for role in ctx.guild.roles if role.is_assignable() and r in role.name.lower()]
            closest=difflib.get_close_matches(role.lower(), roles,n=1, cutoff=0)
            if closest:
                for role in ctx.guild.roles:
                    if role.name.lower() == closest[0].lower():
                        rr=role
                if rr.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                    return await util.send_issue(ctx, f"You cannot edit a role that is higher than your top role!")
                if rr.position >= ctx.guild.me.top_role.position:
                    return await util.send_issue(ctx, f"I don't have access to that role since it is higher than me!")
                if ctx.author.id == ctx.guild.owner.id:
                    pass
                if not role.is_assignable():
                    return await util.send_error(ctx, f"I can't give a ``managed`` role.")
                else:
                    if ctx.guild.id in self.guildTasks:
                        return await util.send_issue(ctx, f'A ``role bots`` is already in progress!')
                    else:
                        self.guildTasks.append(ctx.guild.id)
                        time = datetime.timedelta(seconds=len([i for i in ctx.guild.members if i.bot and not rr in i.roles]))
                        totalTime = humanize.naturaldelta(time)
                        await util.send_blurple(ctx, f"Attempting to role ``{len([i for i in ctx.guild.members if i.bot and not rr in i.roles])} bots`` with the role: {role.mention}. This will take approximatley: {totalTime}")
                        count = 0
                        for i in ctx.guild.members:
                            if i.bot and not rr in i.roles:
                                try:
                                    await i.add_roles(rr)
                                    count +=1
                                except:
                                    pass
                        self.guildTasks.remove(ctx.guild.id)
                        return await ctx.reply(embed=discord.Embed(description=f"Completed giving the role: {rr.mention} to: ``{count} bots`` in: **{totalTime}**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))       
        if role is None:
            embed = discord.Embed(title="Group Command: role bots", description="Give a role to all bots in your server\n```Syntax: role bots [role_name]\nExample: role bots botrole```", color = discord.Color.blurple())
            embed.set_author(name="role bots help", icon_url=ctx.me.avatar.url)
            embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('role').walk_commands()])} ・ role bots")
            return await ctx.send(embed=embed)
        else:
            return await util.send_issue(ctx, f"I could not find the role: ``{role}``")

    @bots.command(
        usage = 'manage_roles',
        description = 'Remove a role from all bots in your server',
        brief = 'role_name',
        help = '```Syntax: role bots remove [role_name]\nExample: role bots remove bot_role```'
    )
    @commands.has_permissions(manage_roles=True)
    async def remove(self, ctx, *, role: typing.Union[ discord.Role, str]):
        if isinstance(role, discord.Role):
            r=role
            if r.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                return await util.send_issue(ctx, f"You cannot give a role that is higher than your top role!")
            if r.position >= ctx.guild.me.top_role.position:
                return await util.send_issue(ctx, f"I don't have access to that role since it is higher than me!")
            if ctx.author.id == ctx.guild.owner.id:
                pass
            if not role.is_assignable():
                return await util.send_error(ctx, f"I can't access a ``managed`` role.")
            else:
                    time = datetime.timedelta(seconds=len([i for i in ctx.guild.members if i.bot and not r in i.roles]))
                    totalTime = humanize.naturaldelta(time)
                    await util.send_blurple(ctx, f"Attempting to remove ``{len([i for i in ctx.guild.members if i.bot and r in i.roles])} bots`` with the role: {role.mention}. This will take approximatley: {totalTime}")
                    count = 0
                    for i in ctx.guild.members:
                        if i.bot and r in i.roles:
                            try:
                                await i.remove_roles(r)
                                count +=1
                            except:
                                pass
                    return await ctx.reply(embed=discord.Embed(description=f"Completed removing the role: {r.mention} from: ``{count} bots`` in: **{totalTime}**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
        if isinstance(role, str):
            r=role.lower()
            roles=[role.name.lower() for role in ctx.guild.roles if role.is_assignable() and r in role.name.lower()]
            closest=difflib.get_close_matches(role.lower(), roles,n=1, cutoff=0)
            if closest:
                for role in ctx.guild.roles:
                    if role.name.lower() == closest[0].lower():
                        rr=role
                if rr.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                    return await util.send_issue(ctx, f"You cannot edit a role that is higher than your top role!")
                if rr.position >= ctx.guild.me.top_role.position:
                    return await util.send_issue(ctx, f"I don't have access to that role since it is higher than me!")
                if ctx.author.id == ctx.guild.owner.id:
                    pass
                if not role.is_assignable():
                    return await util.send_error(ctx, f"I can't access a ``managed`` role.")
                else:
                        time = datetime.timedelta(seconds=len([i for i in ctx.guild.members if i.bot and rr in i.roles]))
                        totalTime = humanize.naturaldelta(time)
                        await util.send_blurple(ctx, f"Attempting to remove ``{len([i for i in ctx.guild.members if i.bot and rr in i.roles])} bots`` with the role: {role.mention}. This will take approximatley: {totalTime}")
                        count = 0
                        for i in ctx.guild.members:
                            if i.bot and rr in i.roles:
                                try:
                                    await i.remove_roles(rr)
                                    count +=1
                                except:
                                    pass
                        return await ctx.reply(embed=discord.Embed(description=f"Completed giving removing role: {rr.mention} from: ``{count} bots`` in: **{totalTime}**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))       



    @humans.command(
        invoke_without_command=True,
        usage = 'manage_roles',
        description = 'Remove a role from all humans in your server',
        brief = 'role_name',
        help = '```Syntax: role humans remove [role_name]\nExample: role humans remove Members```'
    )
    @commands.has_permissions(manage_roles=True)
    async def remove(self, ctx, *, role: typing.Union[ discord.Role, str]):
        if isinstance(role, discord.Role):
            r=role
            if r.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                return await util.send_issue(ctx, f"You cannot give a role that is higher than your top role!")
            if r.position >= ctx.guild.me.top_role.position:
                return await util.send_issue(ctx, f"I don't have access to that role since it is higher than me!")
            if ctx.author.id == ctx.guild.owner.id:
                pass
            if not role.is_assignable():
                return await util.send_error(ctx, f"I can't access a ``managed`` role.")
            else:
                    time = datetime.timedelta(seconds=len([i for i in ctx.guild.members if not i.bot and r in i.roles]))
                    totalTime = humanize.naturaldelta(time)
                    await util.send_blurple(ctx, f"Attempting to remove ``{len([i for i in ctx.guild.members if not i.bot and r in i.roles])} humans`` with the role: {role.mention}. This will take approximatley: {totalTime}")
                    count = 0
                    for i in ctx.guild.members:
                        if not i.bot and r in i.roles:
                            try:
                                await i.remove_roles(r)
                                count +=1
                            except:
                                pass
                    return await ctx.reply(embed=discord.Embed(description=f"Completed removing the role: {r.mention} from: ``{count}`` humans in: {totalTime}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
        if isinstance(role, str):
            r=role.lower()
            roles=[role.name.lower() for role in ctx.guild.roles if role.is_assignable() and r in role.name.lower()]
            closest=difflib.get_close_matches(role.lower(), roles,n=1, cutoff=0)
            if closest:
                for role in ctx.guild.roles:
                    if role.name.lower() == closest[0].lower():
                        rr=role
                if rr.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                    return await util.send_issue(ctx, f"You cannot edit a role that is higher than your top role!")
                if rr.position >= ctx.guild.me.top_role.position:
                    return await util.send_issue(ctx, f"I don't have access to that role since it is higher than me!")
                if ctx.author.id == ctx.guild.owner.id:
                    pass
                if not role.is_assignable():
                    return await util.send_error(ctx, f"I can't give a ``managed`` role.")
                else:
                        time = datetime.timedelta(seconds=len([i for i in ctx.guild.members if not i.bot and rr in i.roles]))
                        totalTime = humanize.naturaldelta(time)
                        await util.send_blurple(ctx, f"Attempting to remove ``{len([i for i in ctx.guild.members if not i.bot and rr in i.roles])} humans`` with the role: {role.mention}. This will take approximatley: **{totalTime}**")
                        count=0
                        for i in ctx.guild.members:
                            if not i.bot and rr in i.roles:
                                try:
                                    await i.remove_roles(rr)
                                    count+=1
                                except:
                                    pass
                        return await ctx.reply(embed=discord.Embed(description=f"Completed removing the role: {rr.mention} from: ``{count} humans`` in: **{totalTime}**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))       

        else:
            return await util.send_issue(ctx, f"I could not find the role: ``{role}``")


    @commands.command(name='setme', aliases=['setup'], description="setup the moderation system")
    @commands.has_permissions(administrator=True)
    async def setme(self, ctx):
        async with ctx.typing():
            check = await self.guilddb.find_one({ "guild_id": ctx.guild.id })
            if check:
                jail_role = check['jail_role']
                recieverole = discord.utils.get(ctx.guild.roles, id = jail_role)
                if not recieverole:
                    await ctx.guild.create_role(name="bjailed")
                    recieverole2 = discord.utils.get(ctx.guild.roles, name="bjailed")
                    await self.guilddb.update_one({ "guild_id": ctx.guild.id }, { "$set": { "jail_role": recieverole2.id }})
                    jail_deny_voice = discord.PermissionOverwrite(connect=False)
                    jail_allow = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    jail_deny_text = discord.PermissionOverwrite(read_messages=False)
                    for channel in ctx.guild.channels:
                        if isinstance(channel, discord.TextChannel):
                            await channel.set_permissions(recieverole, overwrite=jail_deny_text)
                        elif isinstance(channel, discord.VoiceChannel):
                            await channel.set_permissions(recieverole, overwrite=jail_deny_voice)
                    await ctx.send("added new jailrole since the other was missing")

                jail_channel = check['jail_channel']
                recievechan = discord.utils.get(ctx.guild.text_channels, id=jail_channel)
                if not recievechan:
                    await ctx.guild.create_text_channel(name="blamejail")
                    recievechan2 = discord.utils.get(ctx.guild.text_channels, name="blamejail")
                    await self.guilddb.update_one({ "guild_id": ctx.guild.id }, { "$set": { "jail_channel": recievechan2.id}})
                    jail_deny_voice2 = discord.PermissionOverwrite(connect=False)
                    jail_allow2 = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    jail_deny_text2 = discord.PermissionOverwrite(read_messages=False)

                    for channel in ctx.guild.channels:
                        if isinstance(channel, discord.TextChannel):
                            if channel == recievechan2:
                                await channel.set_permissions(recieverole, overwrite=jail_allow2)
                                await channel.set_permissions(ctx.guild.default_role, overwrite=jail_deny_text2)
                            else:
                                await channel.set_permissions(recieverole, overwrite=jail_deny_text2)
                        elif isinstance(channel, discord.VoiceChannel):
                            await channel.set_permissions(recieverole, overwrite=jail_deny_voice2)
                    await ctx.send("added new jailchannel since the other was missing")
                elif recieverole and recievechan:
                    return await ctx.send("Your jail role and channel alreasy exists")

            else:
                await ctx.guild.create_role(name="bjailed")
                recrole = discord.utils.get(ctx.guild.roles, name="bjailed")
                await ctx.guild.create_text_channel(name="blamejail")
                recchan = discord.utils.get(ctx.guild.text_channels, name="blamejail")
                first = discord.Embed(description="adding jail role")
                await asyncio.sleep(1)
                firstsend = await ctx.send(embed=first)
                await asyncio.sleep(0.9)
                second = discord.Embed(description="adding jail channel")
                await asyncio.sleep(1)
                await firstsend.edit(embed=second)
                await asyncio.sleep(0.9)
                await self.guilddb.insert_one({
                    "guild_id": ctx.guild.id,
                    "jail_role": recrole.id,
                    "jail_channel": recchan.id
                })
                await asyncio.sleep(1)
                finder = await self.guilddb.find_one({"guild_id": ctx.guild.id})
                jail_channel = finder['jail_channel']
                jail_role = finder['jail_role']
                scraprole = discord.utils.get(ctx.guild.roles, id = jail_role)
                scrapchan = discord.utils.get(ctx.guild.text_channels, id=jail_channel)
                jail_deny_voice2 = discord.PermissionOverwrite(connect=False)
                jail_allow2 = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                jail_deny_text2 = discord.PermissionOverwrite(read_messages=False)
                for channel in ctx.guild.channels:
                    if isinstance(channel, discord.TextChannel):
                        if channel == scrapchan:
                            await channel.set_permissions(scraprole, overwrite=jail_allow2)
                            await channel.set_permissions(ctx.guild.default_role, overwrite=jail_deny_text2)
                        else:
                            await channel.set_permissions(scraprole, overwrite=jail_deny_text2)
                    elif isinstance(channel, discord.VoiceChannel):
                        await channel.set_permissions(scraprole, overwrite=jail_deny_voice2)
                last = discord.Embed(description="jail has been successfully set up")
                await asyncio.sleep(1)
                await firstsend.edit(embed=last)


    @commands.command(name='jail', description='takes users roles and gives them a jailed role', brief='member', usage='moderate_members')#                                                       MARIA DB MAKE IT FUCKIN MONGO NIGGER
    @commands.has_permissions(moderate_members=True)
    async def jail(self, ctx, member: discord.Member=None):
        async with ctx.typing():

            check = await self.guilddb.find_one({ "guild_id": ctx.guild.id})
            if check:

                """Syntax: !jail <mention/id>
                Example: !jail @cop#0001"""
                roles=[]
                obj=[]
                if member == None:
                    return await util.send_issue(ctx, f"Please specify a member to jail!")
                find = await self.userdb.find_one({"guild_id": ctx.guild.id, "user_id": member.id})
                if find:
                    return await util.send_issue(ctx, f"**User: {member.mention} is already jailed! Use ``{ctx.prefix}unjail`` to unjail them!")
            

                jailfind = check['jail_role']
                jail_role = discord.utils.get(ctx.guild.roles, id=jailfind)
                if ctx.author.top_role.position <= member.top_role.position and ctx.author != ctx.guild.owner:
                    return await util.send_error(ctx, f"You can't jail someone higher than you!")
                if member == ctx.author:
                    return await ctx.send("you can't jail yourself you moron!")
                member_roles = [role for role in member.roles if not role.is_assignable()]
                for role in member.roles:
                    roles.append(role.id)
                try:
                    await member.edit(roles=member_roles)
                except:
                    pass
                try: 
                    print("aye")
                    await member.add_roles(jail_role, reason=f"Jailed by: {ctx.author}")
                except:
                    return await util.send_issue(ctx, f"Jail hasn't been setup yet. Use ``{ctx.prefix}setme`` to do so.")
                new_lst=(','.join(str(a)for a in roles))
                newroles=f"{new_lst}"
                await self.userdb.insert_one({
                    "guild_id": ctx.guild.id,
                    "user_id": member.id,
                    "role_ids": newroles})
                try:
                    chanfind = await self.guilddb.find_one({'guild_id': ctx.guild.id})
                    chan = chanfind['jail_channel']
                    getchan = ctx.guild.get_channel(chan)
                    await getchan.send(f"{member.mention}, looks like you've been jailed. To prevent this, please follow the rules and do as said. If you'd like to be unjailed please contact a a moderator or admin to do so :thumbsup:")
                except Exception as e:
                    print(e)
                    pass
                await util.send_blurple(ctx, f"{ctx.author.mention} **jailed** {member.mention}")
            else:
                return await util.send_issue(ctx, f"Jail hasn't been setup yet. Use ``{ctx.prefix}setme`` to do so.")

    @commands.command(name='unjail', description='unjail a jailed user and restore their roles', brief='member / all', usage='moderate_members')#                                                       MARIA DB MAKE IT FUCKIN MONGO NIGGER
    @commands.has_permissions(moderate_members=True)
    async def unjail(self, ctx, member: typing.Union[discord.Member, str]=None):
        """Syntax: !unjail <mention/id/all>
        Example: !unjail @cop#0001"""
        async with ctx.typing():
            check = await self.guilddb.find_one({ "guild_id": ctx.guild.id})
            if check:
                obj=[]
                if member == None:
                    return await util.send_issue(ctx, f"Please specify a member to unjail!")
                if isinstance(member, discord.Member):
                    if member == ctx.author:
                        return await ctx.send("you can't unjail yourself you moron!")
                    
                    if not await self.userdb.find_one({ "guild_id": ctx.guild.id, "user_id": member.id}):
                        return await util.send_issue(ctx, f"{member.mention} is not currently jailed!")
                    getjailrole = check['jail_role']
                    jail_role = discord.utils.get(ctx.guild.roles, id=getjailrole)
                    try:
                        await member.remove_roles(jail_role)
                    except:
                        return await util.send_issue(ctx, f"Jail hasn't been setup yet. Use ``{ctx.prefix}setme`` to do so.")
                    data=await self.userdb.find_one({"guild_id": ctx.guild.id, "user_id": member.id})
                    if not data:
                        return await util.send_issue(ctx, f"That user is not currently jailed!")

                    roles=data['role_ids']
                    roles=roles.split(",")
                    new_roles = []
                    for r in roles:
                        role = discord.utils.get(ctx.guild.roles, id=int(r))
                        new_roles.append(role)

                    await member.edit(roles=new_roles, reason=f"Unjailed by: {ctx.author}")
                    await self.userdb.delete_one({ "guild_id": ctx.guild.id, "user_id": member.id})
                    await util.send_blurple(ctx, f"{ctx.author.mention}: unjailed {member.mention}")

            else:
                return await util.send_issue(ctx, f"Jail hasn't been setup yet. Use ``{ctx.prefix}setme`` to do so.")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def jailed(self, ctx):
        async with ctx.typing():
            check = await self.guilddb.find_one({ "guild_id": ctx.guild.id})
            if check:
                rows = []
                jailroler = check['jail_role']
                jailrole = discord.utils.get(ctx.guild.roles, id=jailroler)
                content = discord.Embed(title = f"Jailed members in {ctx.guild.name}", description = "", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                content.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)

                if jailrole:
                    try:
                        for count, m in enumerate(jailrole.members, start=1):
                            rows.append(f"**{count}.)** {m.mention} - ``{m.id}`` ")
                            content.set_footer(text=f"Entries: {len(jailrole.members)}/{len(rows)}", icon_url=ctx.guild.icon.url)
                        await util.send_as_pages(ctx, content, rows)
                    except:
                        return await util.send_blurple(ctx, f"There is no one jailed.")

                else:
                    return await util.send_blurple(ctx, f"The jail role is missing. Please use the ``setme`` command.")
            else:
                return await util.send_blurple(ctx, f"The jail module has not been setup properly. Please use the ``setme`` command.")


    @commands.command(name='ban', aliases=['deport'], description='Ban a user', brief='member/user, reason[optional]', usage='ban_members')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: typing.Union[discord.Member, discord.User]=None, *, reason:str=None):
        """```Syntax: !ban <user> <reason>
        Example: !ban @cop racism```"""
        try:
            if not reason:
                reason=f"{ctx.author} - No Reason Provided"
            if not member:
                return await util.send_issue(ctx, 'Please provide a user to ban!')
            if member in ctx.guild.members:
                if ctx.author.id == ctx.guild.owner.id:
                    pass
                if member.id == ctx.guild.owner.id:
                    return await util.send_issue(ctx, "You can't ban the server owner..")
                if ctx.author.top_role == member.top_role:
                    return await util.send_issue(ctx, "You cant' ban someone who has the same permissions as you!")
                if ctx.author.top_role < member.top_role:
                    return await util.send_issue(ctx, "You cannot ban someone higher than you!")
                else:
                    if member.premium_since:
                        content = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                        content.set_author(name='Ban booster?', icon_url='https://cdn.discordapp.com/emojis/921807005591670856.gif?size=44&quality=lossless')
                        content.description = f"{member.mention} is currently **boosting**. Are you sure you want to **ban** them?"
                        msg = await ctx.send(embed=content)
                        async def confirm():
                            check = await self.bans.find_one({'guild_id': ctx.guild.id})
                            if check:
                                message = check['banmsg']
                                if message.startswith("(embed)"):
                                    message = message.replace('(embed)', '')
                                    message = await util.welcome_vars(user=member, params=message)
                                    if "content:" in message.lower():
                                        em = await util.to_embed(ctx, params=message)
                                        msg = await util.to_content(ctx, params=message)
                                        await ctx.guild.ban(member, reason=reason)
                                        return await msg.edit(content=msg, embed=em, view=None)
                                    else:
                                        message = message.replace('(embed)', '')
                                        message = await util.welcome_vars(user=member, params=message)
                                        em = await util.to_embed(ctx, params=message)
                                        await ctx.guild.ban(member, reason=reason)
                                        return await msg.edit(embed=em, view=None)
                                elif message.startswith("(embed)"):
                                    message = await util.welcome_vars(user=member, params=message)
                                    await ctx.guild.ban(member, reason=reason)
                                    return await msg.edit(message, view=None)
                            else:
                                await ctx.guild.ban(member, reason=reason)
                                await util.send_blurple(ctx, f"Banned {member}")
                                return await msg.edit(view=None)
                        async def cancel():
                            await util.send_issue(ctx, "Ban process cancelled!")
                            return await msg.delete()
                        confirmed:bool = await cop_is_gae.confirm(self, ctx, msg)
                        if confirmed:
                            await confirm()
                        else:
                            await cancel()
                    else:
                        check = await self.bans.find_one({'guild_id': ctx.guild.id})
                        if check:
                            message = check['banmsg']
                            if message.startswith("(embed)"):
                                message = message.replace('(embed)', '')
                                message = await util.welcome_vars(user=member, params=message)
                                if "content:" in message.lower():
                                    em = await util.to_embed(ctx, params=message)
                                    msg = await util.to_content(ctx, params=message)
                                    await ctx.send(content=msg, embed=em)
                                    return await ctx.guild.ban(member, reason=reason)
                                else:
                                    message = message.replace('(embed)', '')
                                    message = await util.welcome_vars(user=member, params=message)
                                    em = await util.to_embed(ctx, params=message)
                                    await ctx.send(embed=em)
                                    return await ctx.guild.ban(member, reason=reason)
                            elif not message.startswith("(embed)"):
                                message = await util.welcome_vars(user=member, params=message)
                                await ctx.guild.ban(member, reason=reason)
                                return await ctx.send(message)
                        else:
                            await util.send_blurple(ctx, f"Banned {member}")
                            return await ctx.guild.ban(member, reason=reason)
            else:
                check = await self.bans.find_one({'guild_id': ctx.guild.id})
                if check:
                    message = check['banmsg']
                    if message.startswith("(embed)"):
                        message = message.replace('(embed)', '')
                        message = await util.welcome_vars(user=member, params=message)
                        if "content:" in message.lower():
                            em = await util.to_embed(ctx, params=message)
                            msg = await util.to_content(ctx, params=message)
                            await ctx.send(content=msg, embed=em)
                            return await ctx.guild.ban(member, reason=reason)
                        else:
                            message = message.replace('(embed)', '')
                            message = await util.welcome_vars(user=member, params=message)
                            em = await util.to_embed(ctx, params=message)
                            await ctx.send(embed=em)
                            return await ctx.guild.ban(member, reason=reason)
                    elif not message.startswith("(embed)"):
                        message = await util.welcome_vars(user=member, params=message)
                        await ctx.send(message)
                        return await ctx.guild.ban(member, reason=reason)
                else:
                    await util.send_blurple(ctx, f"Banned {member}")
                    return await ctx.guild.ban(member, reason=reason)
        except Exception as e:
            return await util.send_issue(ctx, f"{member} is already banned!")



    @commands.command(name='kick', description='Kick User(s)', brief='users', usage='kick_members')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, *discord_users):
        """```Syntax: !kick <@users>
        Example: !kick @cop @prada @rival```"""
        if not discord_users:
            return await ctx.send(embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"please specify a user"))

        for discord_user in discord_users:
            user = await util.get_member(ctx, discord_user)
            if user is None:
                try:
                    user = await self.bot.fetch_user(int(discord_user))
                except (ValueError, discord.NotFound):
                    await ctx.send(
                        embed=discord.Embed(
                            description=f"<:n_:921559211366838282> Invalid user or id `{discord_user}`",
                            color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16),
                        )
                    )
                    continue

            if user.id == 133311691852218378:
                return await ctx.send("no.")
            member=user
            if user in ctx.guild.members:
                if ctx.author.id == ctx.guild.owner.id:
                    pass
                else:
                    if ctx.author.id != ctx.guild.owner.id:
                        if member.id == ctx.guild.owner.id:
                            return await ctx.send(embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"<:n_:921559211366838282> {ctx.author.mention}: **you can't {ctx.command.name} the owner**"))
                        if ctx.author.top_role == member.top_role:
                            return await ctx.send(embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"<:n_:921559211366838282> {ctx.author.mention}: **you can't {ctx.command.name} someone who has the same permissions as you**"))
                        if ctx.author.top_role < member.top_role:
                            return await ctx.send(embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"<:n_:921559211366838282> {ctx.author.mention}: **you can't {ctx.command.name} someone higher than yourself**"))
            else:
                pass

            # confirmation dialog for guild members
            if isinstance(user, discord.Member):
                try:
                    await self.send_Kick_confirmation(ctx, user)
                except:
                    await ctx.send(embed=discord.Embed(description=f"{ctx.author.mention}: **i cannot kick that member**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
            else:
                await ctx.send(
                    embed=discord.Embed(
                        description=f"<:n_:921559211366838282> Invalid user or id `{discord_user}`",
                        color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16),
                    )
                )



    async def send_Kick_confirmation(self, ctx, user):
        content = discord.Embed(title="<:hammer:940737261761335296> Kick user?", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
        content.description = f"{user.mention}\n**{user.name}#{user.discriminator}**\n{user.id}"
        msg = await ctx.send(embed=content)

        async def confirm_Kick():
            try:
                await user.kick(reason=f"User Responsible: {ctx.author}")
                content.title = "<:check:921544057312915498> kicked user"
                content.colour=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)
            except discord.errors.Forbidden:
                content.title = None
                content.description = f"<:yy_yno:921559254677200957> It seems I don't have the permission to kick **{user}** {user.mention}"
                content.colour =int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)
            await msg.edit(embed=content, view=None)

        async def cancel_Kick():
            content.title = "<:yy_yno:921559254677200957> Kick cancelled"
            content.colour=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)
            await msg.edit(embed=content, view=None)

        confirmed:bool = await confirm.confirm(self, ctx, msg)
        if confirmed:
            await confirm_Kick()
        else:
            await cancel_Kick()

    @commands.command(name='unban', description='unban a user', brief='id/name#discriminator, reason[optional]', usage='ban_members')
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: typing.Union[discord.User, int, str], *, reason:str=None):
        """```Syntax: !unban <name#discrim/id> <reason>
        Example: !unban cop#0001```"""
        if isinstance(user, int):
            user_str = f"<@{user}>"
            user = discord.Object(id=user)
        else:
            user_str = user
        
        if isinstance(user, str):
            bans=[]
            async for ban in ctx.guild.bans():
                bans.append(ban)
            try:
                name, tag = user.split('#')
                banned_user = discord.util.get(
                    bans, user__name=name,
                    user__discriminator=tag
                )
            except:
                try:
                    banned_user=discord.util.get(bans, user__name=user)
                except:
                    embed=discord.Embed(description=f"<:n_:921559211366838282> {ctx.author.mention}: *Please format the username like this: \nUsername#0000*", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)).set_footer(text="Prefix = !")
                    await ctx.send(embed=embed)
                    return
            if banned_user is None:
                embed=discord.Embed(description=f"<:n_:921559211366838282> {ctx.author.mention}: **User Not Found**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)).set_footer(text="Prefix = !")
                await ctx.send(embed=embed)
                return
            await ctx.guild.unban(banned_user.user)
            embed = discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention}: **{user_str}** has been unbanned", color=0x43B581)
            await ctx.send(embed=embed)
        try:
            user = self.bot.get_user(user)
        except:
            pass
        if not isinstance(user, str):
            try:
                await ctx.guild.unban(user)
                embed = discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention}: **{user.name}#{user.discriminator}** has been unbanned", color=0x43B581)
                await ctx.send(embed=embed)
            except:
                embed=discord.Embed(description="<:n_:921559211366838282> **User Not Found**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                await ctx.send(embed=embed)

    @commands.hybrid_command(name='bc', description='purge bot msgs', usage="manage_messages")
    @commands.has_permissions(manage_messages=True)
    async def bc(self, ctx):
        def predicate(m):
            return m.author.bot or m.content.startswith(f"{ctx.prefix}")
        await ctx.message.delete()
        deleted=await util.do_removal(ctx, 100, predicate)
        await util.send_blurple(ctx, f" Purged {deleted} messages from bots")


    @commands.command(name='purge', aliases = ['p', 'clear', 'c'], description='purge messages', brief="member/amount/images/amount", usage="manage_messages")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, args:typing.Union[discord.Member, int, str]=None, amount: typing.Optional[int]=None):
        await ctx.message.delete()
        msgs=[]
        if args == None:
            return await ctx.reply(embed=discord.Embed(title="Purge Help", description="!purge @member <amount>\n!purge <amount>\n!purge images <amount>"))
        if isinstance(args, discord.Member):
            if amount:
                search=amount+1
            else:
                search=100
            if search >= 2000:
                return await util.send_no(ctx, f"{ctx.author.mention}: **purge limit is 2000**")
            member=args
            async for m in ctx.channel.history():
                if len(msgs) == search:
                    break
                if m.author == member:
                    msgs.append(m)
            await ctx.channel.delete_messages(msgs)
            #deleted=await util.do_removal(ctx, search, lambda e: e.author == member)
            msg = await util.send_blurple(ctx, f" purged {len(msgs)} messages from {member.mention}")
            await asyncio.sleep(5)
            await msg.delete()
        if isinstance(args, int):
            search=args
            deleted=await util.do_removal(ctx, search, lambda e: True)
            msg1 = await util.send_blurple(ctx, f" purged {deleted} messages")
            await asyncio.sleep(5)
            await msg1.delete()
        if isinstance(args, str):
            msgs=['messages', 'msgs']
            imgs=['imgs', 'images']
            h=['help', 'cmds', 'h']
            if amount is None:
                search=100
            else:
                search=amount
            if args.lower() in msgs:
                def predicate(m):
                    return m.attachments is None
                deleted=await util.do_removal(ctx, search, predicate)
                msg2=await util.send_blurple(ctx, f" **purged `{deleted}` messages that do not contain immages**")
                await asyncio.sleep(5)
                await msg2.delete()
            if args.lower() in h:
                return await ctx.reply(embed=discord.Embed(title="Purge Help", description="!purge @member <amount>\n!purge <amount>\n!purge images <amount>\n!purge messages <amount>"))
            if args.lower() in imgs:
                deleted=await util.do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))
                msg3 = await util.send_blurple(ctx, f" purged {deleted} images")
                await asyncio.sleep(5)
                await msg3.delete()
            else:
                await ctx.reply(embed=discord.Embed(title="Purge Help", description="!purge @member <amount>\n!purge <amount>\n!purge images <amount>"))

    @commands.hybrid_command(name='timeout', aliases=['mute', 'm'], description="Timeout/Mute a user in the server", help="```Syntax: !timeout <member> <time> <reason>\nExample: !timeout @cop 1hour racism```",brief='member, time, reason[optional]', usage='moderate members')
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def timeout(self, ctx: commands.Context, user: discord.Member, time:typing.Optional[str], *, reason: str = "No reason provided"):
        if not user and not time and not reason == None:
            await ctx.send("yes")
        if ctx.author.top_role.position <= user.top_role.position and ctx.author != ctx.guild.owner:
            return await ctx.send(embed=discord.Embed(description=f"<:no:940723951947120650> {user.mention} **is higher then you** {ctx.author.mention}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
        if ctx.author.id == ctx.guild.owner.id:
            pass
        if user == ctx.author:
            return await ctx.send(embed=discord.Embed(description="<:no:940723951947120650> **You can't mute yourself!**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
        if not time:
            time="1hour"
        try:
            rs=reason+f"by {ctx.author}"
            try:
                timeConvert = humanfriendly.parse_timespan(time)
                await user.timeout(discord.utils.utcnow()+datetime.timedelta(seconds=timeConvert), reason=rs)
            except:
                pass
                await user.timeout(discord.utils.utcnow()+datetime.timedelta(seconds=1140), reason=time)
                embed1 = discord.Embed(description=f"<:check:921544057312915498> **muted** {user.mention} | Reason: **{time}**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                return await ctx.send(embed=embed1)
            embed = discord.Embed(description=f"<:check:921544057312915498> **muted** {user.mention} for {time} | Reason: **{reason}**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
            await ctx.send(embed=embed)
            #await user.send(embed=discord.Embed(description=f"**You were muted in {ctx.guild.name} | Reason: {reason}**", color=discord.Color.red()))
        except discord.Forbidden:
            return await ctx.send(embed=discord.Embed(description="<:no:940723951947120650> **This user has a higher or equal role to me. **", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
        except discord.errors.HTTPException:
            return await ctx.reply(embed=discord.Embed(description=f"<:warn:940732267406454845> {ctx.author.mention}: **max mute time is `30days`**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))

    @commands.command(name='untimeout', aliases=['unmute', 'un'], description="Unmutes a user from the server", usage="```Syntax: !untimeout <member> <reason>\nExample: !untimeout @cop#0001```",brief='member, reason', extras={'perms': 'moderate members'})
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def untimeout(self, ctx: commands.Context, user: discord.Member, *, reason: str = "No reason provided"):
        if user == ctx.author:
            return await ctx.send(embed=discord.Embed(description=f"<:no:940723951947120650> {ctx.author.mention}: **You can't unmute yourself!**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
        if not user.is_timed_out():
            return await ctx.send(embed=discord.Embed(description=f"<:no:940723951947120650> {ctx.author.mention}: **That user isn't muted!**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
        
        rs=reason+f"by {ctx.author}"
        await user.timeout(discord.utils.utcnow(), reason=rs)
        embed = discord.Embed(description=f"<:check:921544057312915498> **unmuted**  {user.mention} | Reason: **{reason}**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def uuuunban(self, ctx, *, user=None):

        try:
            user = await commands.converter.UserConverter().convert(ctx, user)
        except:
            await ctx.send("Error: user could not be found!")
            return

        try:
            bans = tuple(ban_entry.user for ban_entry in await ctx.guild.bans())
            if user in bans:
                await ctx.guild.unban(user, reason="Unbanned by "+ str(ctx.author))
            else:
                await ctx.send("User not banned!")
                return

        except discord.Forbidden:
            await ctx.send("I do not have permission to unban!")
            return

        except:
            await ctx.send("Unbanning failed!")
            return

        await ctx.send(f"Unbanned {user.mention} :thumbsup: ")

    @commands.hybrid_command(name='nuke', description="recreate and delete current channel", usage='Guild Owner')
    @commands.guild_only()
    async def nuke(self, ctx):
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id == 714703136270581841:
            counter = 0
            await ctx.send(embed=discord.Embed(title=self.bot.user.name, description=f"Nuking Channel {ctx.channel.name}..."))
            channel_info = [ctx.channel.category, ctx.channel.position]
            channel_id = ctx.channel.id
            await ctx.channel.clone()
            await ctx.channel.delete()
            new_channel = channel_info[0].text_channels[-1]
            await new_channel.edit(position=channel_info[1])
            embed = discord.Embed(timestamp=ctx.message.created_at)
            embed.set_author(name=f"Channel Nuked.", icon_url=ctx.author.display_avatar)
            embed.set_footer(text=f"{ctx.author}")
            embed.set_image(url=self.bot.user.display_avatar)
            await new_channel.send(embed=embed, delete_after=30)
        else:
            await util.send_error(ctx, f"only available to the `guild owner`")


    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def massunban(self, ctx, *, reason=None): 
        if not ctx.author.id == 236522835089031170:
            return await ctx.send("Your guild is not authorized to use this command. Join the discord to find out why. ")
        else:
            if ctx.message.guild == None:
                pass
            else:          
                banlist = [entry async for entry in ctx.guild.bans(limit=10000)] 
                members = [str(f'{users.user} - {users.user.id}') for users in banlist]
                if len(members) == 0:
                    await ctx.send(' theres legit no one banned :thumbsdown: ')
                    return     
                i = discord.Embed(description=' Mass unban starting ', color=0x43B581)
                await ctx.send(embed=i)            
                for users in banlist:
                    try:
                        await ctx.guild.unban(user=users.user)
                    except:
                        pass      

                per_page = 10 
                pages = math.ceil(len(members) / per_page)
                cur_page = 1
                chunk = members[:per_page]
                linebreak = "\n"
                
                em = discord.Embed(title=f"{len(members)} Idiots unbanned:", description=f"{linebreak.join(chunk)}", color=0x43B581)
                em.set_footer(text=f"Page {cur_page}/{pages}:")            
                message = await ctx.send(embed=em)
                await message.add_reaction("◀️")
                await message.add_reaction("▶️")
                active = True

                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
                                # or you can use unicodes, respectively: "\u25c0" or "\u25b6"

                while active:
                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                    
                        if str(reaction.emoji) == "▶️" and cur_page != pages:
                            cur_page += 1
                            if cur_page != pages:
                                chunk = members[(cur_page-1)*per_page:cur_page*per_page]
                            else:
                                chunk = members[(cur_page-1)*per_page:]
                            e = discord.Embed(title=f"{len(members)} Idiots unbanned:", description=f"{linebreak.join(chunk)}",color=0x43B581)
                            e.set_footer(text=f"Page {cur_page}/{pages}:")
                            await message.edit(embed=e)
                            await message.remove_reaction(reaction, user)

                        elif str(reaction.emoji) == "◀️" and cur_page > 1:
                            cur_page -= 1
                            chunk = members[(cur_page-1)*per_page:cur_page*per_page]
                            e = discord.Embed(title=f"{len(members)} Idiots unbanned:", description=f"{linebreak.join(chunk)}", color=0x43B581)
                            e.set_footer(text=f"Page {cur_page}/{pages}:")
                            await message.edit(embed=e)
                            await message.remove_reaction(reaction, user)
                    except asyncio.TimeoutError:
                        active = False


    @commands.command(aliases=['lock'])
    @commands.has_permissions(manage_channels = True)
    async def lockdown(self, ctx,channel:discord.TextChannel=None):
        try:
            if channel == None:
                lock = await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
                embed=discord.Embed(
                    description=f"<:check:921544057312915498> {ctx.channel.mention} is now **locked** for @everyone",
                    color=0x43B581
                )
                await ctx.send(embed=embed)
            else:
                lock = await channel.set_permissions(ctx.guild.default_role, send_messages=False)
                embed=discord.Embed(
                    description=f"<:check:921544057312915498> {ctx.channel.mention} is now **locked** for @everyone",
                    color=0x43B581
                )
                await ctx.send(embed=embed)
        except:
            pass

    @commands.command()
    @commands.has_permissions(manage_channels = True)
    async def unlock(self, ctx,channel:discord.TextChannel=None):
        if channel == None:
            unlock = await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
            embed=discord.Embed(
                description=f"<:check:921544057312915498> {ctx.channel.mention} is now **unlocked** for @everyone",
                color=0x43B581
            )
            await ctx.send(embed=embed)
        else:
            unlock = await channel.set_permissions(ctx.guild.default_role, send_messages=True)
            embed=discord.Embed(
                description=f"<:check:921544057312915498> {ctx.channel.mention} is now **unlocked** for @everyone",
                color=0x43B581
            )
            await ctx.send(embed=embed)

    @commands.group(
        aliases = ['aliases', 'customaliases', 'customalias'],
        usage = 'manage_guild',
        description = 'Create custom server aliases for commands ',
        brief = 'subcommand',
        help = '```Syntax: alias [subcommand] <args> <subarg>\nExample: alias add avatar av '
    )
    async def alias(self, ctx):
        if ctx.invoked_subcommand is None:       
            embed = discord.Embed(title="Group Command: alias", description="Create custom aliases for commands in your server\n```Syntax: alias [subcommand]\nExample: tag add avatar av```", color = discord.Color.blurple())
            embed.set_author(name="alias help", icon_url=ctx.me.avatar.url)
            embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('alias').walk_commands()])} ・ alias backup")
            return await ctx.send(embed=embed)

    @alias.command()
    async def add(self, ctx, command: str, alias: str):
            check = await self.aliases.find_one({"guild_id": ctx.guild.id, "command": str(command)})
            commands = self.bot.get_command(str(command))
            if commands is None:
                return await util.send_error(ctx, f"Command: ``{command}`` does not exist")
            if check:
                aliases = check['aliases']
                if alias in aliases:
                    return await util.send_error(ctx, f"The alias {alias} is already an existing alias for the ``{command}`` command.")

                else:
                    await self.aliases.insert_one({
                        "guild_id": ctx.guild.id,
                        "command": str(command),
                        "aliases": [str(alias)]
                    })
                    return await util.send_blurple(ctx, f"``{alias}`` is now an alias for the command ``{command}``")
            else:
                await self.aliases.insert_one({
                    "guild_id": ctx.guild.id,
                    "command": str(command),
                    "aliases": [str(alias)]
                })
                return await util.send_blurple(ctx, f"``{alias}`` is now an alias for the command ``{command}``")  

    @commands.command(
        aliases = ['bans', 'serverbans'],
        usage = 'Ban members',
        description = "View the servers ban list (limit=100)",
        brief = 'None',
        help = "```Example: banlist"
    )
    @commands.has_permissions(ban_members=True)
    async def banlist(self, ctx):
        bans = [entry.user.name async for entry in ctx.guild.bans(limit=100)]
        totalbans = [entry.user.name async for entry in ctx.guild.bans(limit=10000)]
        ban_reasons = [entry.reason async for entry in ctx.guild.bans(limit=100)]
        here = [f"**{bans}**: ``{ban_reasons}``" for bans, ban_reasons in zip(bans, ban_reasons)]
        content = discord.Embed(description="")
        content.set_author(name=f"{ctx.guild.name}'s ban list", icon_url=ctx.guild.icon.url)
        content.set_footer(text=f'({len(here)} viewable bans, reasons) ∙ ({len(totalbans) - len(here)} unviewable bans) ∙ ({len(totalbans)} total bans)')
        content.set_thumbnail(url=ctx.guild.icon.url)
        content.color = discord.Color.blurple()
        rows = []

        for count, i in enumerate(here, start=1):
            rows.append(f"``{count})`` {i}")
        await util.send_as_pages(ctx, content, rows)

    @commands.command(
        aliases = ['bots', 'serverbots'],
        usage = "Send messages",
        description = "View all the bots in the server",
        brief = 'None',
        help = "```Example: bots```"
    )
    async def botlist(self, ctx):
        rows = []
        content = discord.Embed(description="", timestamp=ctx.message.created_at)
        content.set_author(name=f"{ctx.author.display_name}", icon_url=ctx.author.avatar)
        content.set_thumbnail(url=ctx.guild.icon.url)
        content.color = discord.Color.blurple()
        for m in ctx.guild.members:
            if m.bot:
                rows.append(f" {m.mention} - ``{m.id}``")
                content.set_footer(text=f"({len([m for m in ctx.guild.members if m.bot])} Total bots) • ({len([m for m in ctx.guild.members if m.bot and m.public_flags.verified_bot])} Verified) • ({len([m for m in ctx.guild.members if m.bot and not m.public_flags.verified_bot])} Unverified)")
        await util.send_as_pages(ctx, content, rows)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def deafen(self, ctx, member: discord.Member=None):
        try:
            if member:
                if member.voice:
                    if member.top_role.position > ctx.author.top_role.position:
                        return await ctx.send("You cannot deafen someone higher than you")
                    else:
                        await member.edit(deafen=True)
                        return await ctx.send(f"{member} has been deafened")
                else:
                    return await ctx.send("theyre not connected")
            else:
                return await ctx.send("Please give a member to deafen")
        except Exception as e:
            print(e)

    @commands.command(
        aliases = ['dhoist', 'dehoist'],
        usage = 'Manage nicknames, Manage server',
        description = "Dehoist all hoisted nicknames within a role such as, nicknames that begin with !, ?, and special characters",
        brief = 'role',
        help = "```Syntax: dehoistnames [role]\nExample: dehoistnames @Members\nNote -> This only dehoists member's nicknames within the role.```"
    )
    @commands.has_permissions(manage_nicknames=True, manage_guild=True)
    async def dehoistnames(self, ctx, role: discord.Role=None):
        try:
            if role==None:
                return await ctx.send("Please be sure to provide a role.")
            else:
                count = 0
                for member in role.members:
                    count = count + 1
                    time_take = count / 20
                    break
                await ctx.send(f"```Analyzing {len(role.members)} members within role: {role.name}\nWill take approximatley: {time_take} minutes```")
                await ctx.message.add_reaction("✅")

                for member in role.members:
                    hoisted = ['!', '?']
                    if str(member.nick).startswith(tuple(hoisted)):
                        await member.edit(nick=member.nick.replace("!" or '?', ''), reason=f"Dehoisting nicknames within role: [ {role.name} ]. Author - {ctx.message.author}")
                        await asyncio.sleep(3)
        except:
            pass

    @commands.command(
        aliases=['ri', 'inforole', 'roleinformation', 'rinfo'],
        usage = 'Manage roles',
        description = 'View certain information upon the given role',
        brief = 'role',
        help = '```Syntax: roleinfo [role]\nExample: roleinfo @Owner```'
        )
    async def roleinfo(self, ctx, *, role: discord.Role = None):
        if role is None:
            role = ctx.author.top_role
        guild = ctx.guild
        since_created = (ctx.message.created_at - role.created_at).days
        role_created = role.created_at.strftime("%d %b %Y %H:%M")
        created_on = "{} ({} days ago)".format(role_created, since_created)
        users = len([x for x in guild.members if role in x.roles])
        if str(role.colour) == "#000000":
            colour = "#000000"
            colour = ("#%06x" % random.randint(0, 0xFFFFFF))
            color = int(colour[1:], 16)
        else:
            colour = str(role.colour).upper()
            color = role.colour
        embed = discord.Embed()
        embed.add_field(name='**Role Name:**', value=f"{role.name}", inline=False)
        embed.add_field(name='**Role ID:**', value=f"{role.id}", inline=False)
        embed.add_field(name="**Users In Role:**", value=f"{users}", inline=False)
        embed.add_field(name="**Mentionable:**", value=f"{role.mentionable}", inline=True)
        embed.add_field(name="**Hoisted:**", value=f"{role.hoist}", inline=True)
        embed.add_field(name="**Position:**", value=f"{role.position}", inline=False)
        embed.add_field(name="**Managed:**", value=f"{role.managed}", inline=True)
        embed.add_field(name="**Colour:**", value=f"{colour}", inline=True)
        embed.add_field(name='**Creation Date:**', value=f"{created_on}", inline=False)
        embed.set_thumbnail(url=f"{ctx.guild.icon.url}")
        embed.set_author(name=f"{ctx.guild.name}", icon_url=ctx.guild.icon.url)
        embed.set_footer(text="Requested by {}".format(ctx.message.author))
        await ctx.send(embed=embed)


    @commands.command(
        aliases = ['inr', 'ir', 'inrol'],
        usage = 'Manage roles',
        description = 'View the members and amount within the given role',
        brief = 'role',
        help = "```Syntax: inrole [role]\nExample: inrole @Users```"
    )
    @commands.has_permissions(manage_roles=True)
    async def inrole(self, ctx, *, r: typing.Union[ discord.Role, str ]=None):
        if r == None:
            await util.send_command_help(ctx)
        if isinstance(r, discord.Role):
            role=r
            content = discord.Embed(title=f"Members in role: {role.name}")
            content.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            rows = []
            for member in role.members:
                rows.append(f"{member.mention}")
            content.description=rows
            content.set_footer(text=f"{len(role.members)} member(s) ∙ {ctx.guild.name}")
            content.color = discord.Color.blurple()
            await util.send_as_pages(ctx, content, rows)
        if isinstance(r, str):
            lis=[]
            for rr in ctx.guild.roles:
                if r in str(rr.name) or r.lower() in str(rr.name).lower():
                    role=rr
                    content = discord.Embed(title=f"Members in role: {role.name}")
                    content.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
                    rows = []
                    for member in role.members:
                        if len(role.members) > 200:
                            return await ctx.send("Too large")
                        else:
                            pass
                        rows.append(f"{member.mention}")
                    content.color = discord.Color.blurple()
                    content.set_footer(text=f"{len(role.members)} member(s) ∙ {ctx.guild.name}")
                    await util.send_as_pages(ctx, content, rows)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def undeafen(self, ctx, member: discord.Member=None):
        try:
            if member:
                if member.voice:
                    if member.top_role.position > ctx.author.top_role.position:
                        return await ctx.send("You cannot undeafen someone higher than you")
                    else:
                        await member.edit(deafen=False)
                        return await ctx.send(f"{member} has been undeafened")
                else:
                    return await ctx.send("not connected")
            else:
                return await ctx.send("Please give a member to undeafen")
        except Exception as e:
            print(e)

async def setup(client): 
   await client.add_cog(mod(client))