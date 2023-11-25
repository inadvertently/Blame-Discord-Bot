import discord, typing
from discord.ext import commands
import Core.utils as util
from datetime import datetime, date
from Core.utils import get_theme

class fperms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fakeperms = self.bot.db['fakeperms']
        self.errorcol = 0xA90F25 # error color
        self.urgecolor = 0xF3DD6C # exclamation color
        self.success = discord.Colour.blurple() #theme
        self.checkmoji = "<:blurple_check:921544108252741723>" # success emoji
        self.xmoji = "<:yy_yno:921559254677200957>" # unsuccessful emoji
        self.urgentmoji = "<:n_:921559211366838282>" # exclamation emoji

    @commands.group(aliases = ['fp', 'fake', 'f'])
    async def fakeperms(self,ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Command: fakeperms", description="Allow a certain user a role to have perms through the bot rather than the server\n```Syntax: fakeperms [subcommand] <argument>\nExample: fakeperms add @jacob ban_members```", color = discord.Color.blurple())
                embed.set_author(name="fakeperms help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('fakeperms').walk_commands()])} ・ fakeperms")
                return await ctx.send(embed=embed)
        except Exception as e:
            print(e)

    @fakeperms.command(
        aliases = ['create'],
        description = 'Allow a certain user a role to have perms through the bot rather than the server',
        brief = 'member, role',
        usage = 'administrator',
        help = '```Syntax: fakeperms add [argument] <permission>\nExample: fakeperms add @jacob ban_members```'
    )
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, arg: typing.Union[discord.Role, discord.Member], permission):
        permissions = ['ban_members', 'kick_members', 'administrator', 'manage_roles', 'manage_channels', 'moderate_members', 'manage_nicknames', 'manage_messages']
        if permission.lower() not in permissions:
            return await ctx.send('That fake permission does not exist')
        check = await self.fakeperms.find_one({"guild_id": ctx.guild.id, 'object': arg.id})
        if check:
            if permission.lower() in check['fakeperms']:
                return await util.send_error(ctx, f"``{permission.lower()}`` is already a fake permission for {arg.mention}")
            else:
                await self.fakeperms.update_one({"guild_id": ctx.guild.id, 'object': arg.id}, { "$push": { "fakeperms": str(permission.lower())}})
                return await util.send_blurple(ctx, f"<:check:921544057312915498>: ``{permission.lower()}`` has been added to {arg.mention}")
        else:
            await self.fakeperms.insert_one({"guild_id": ctx.guild.id, 'object': arg.id, "fakeperms": [str(permission.lower())], "creator": ctx.author.id, 'time': datetime.now()})
            return await util.send_blurple(ctx, f"<:check:921544057312915498>: ``{permission.lower()}`` has been added to {arg.mention}")

    @fakeperms.command(
        aliases = ['rem', 'del', 'delete'],
        description = "Removes a certain fake permission from the role or member provided",
        brief = 'member, role, permission',
        usage = 'administrator',
        help = '```Syntax: fakeperms remove [argument] <permission>\nExample: fakeperms remove @jacob ban_members```'
    )
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, arg: typing.Union[discord.Role, discord.Member], permission):
        permissions = ['ban_members', 'kick_members', 'administrator', 'manage_roles', 'manage_channels', 'moderate_members', 'manage_nicknames', 'manage_messages']
        if permission.lower() not in permissions:
            return await ctx.send('That fake permission does not exist')
        check = await self.fakeperms.find_one({"guild_id": ctx.guild.id, 'object': arg.id})
        if permission.lower() in check['fakeperms']:
            await self.fakeperms.update_one({ "guild_id": ctx.guild.id, 'object': arg.id}, {"$pull": {"fakeperms": str(permission.lower())}})
            return await util.send_blurple(ctx, f"<:check:921544057312915498>: ``{permission.lower()}`` is no longer a fake permission for {arg.mention}")
        else:
            return await util.send_error(ctx, f"``{permission.lower()}`` is not an existing fake permission for {arg.mention}")

    @fakeperms.command(
        aliases = ['lookup', 'details'],
        description = "Get certain info on a member/roles fake permissions",
        brief = "member, role",
        usage = 'None',
        help = '```Syntax: fakeperms info [member]\nExample: fakeperms info @jacob```'
    )
    async def info(self, ctx, arg: typing.Union[discord.Role, discord.Member]):
        check = await self.fakeperms.find_one({"guild_id": ctx.guild.id, 'object': arg.id})
        if check:
            try:
                get_arg = ctx.guild.get_role(check['object'])
            except:
                pass
                get_arg = ctx.guild.get_member(check['object'])
            desc = ""
            for i in check['fakeperms']:
                desc += f"{i}, "
            embed = discord.Embed(title=get_arg, color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
            embed.add_field(name='Creator', value=get_arg)
            embed.set_author(name=get_arg, icon_url=ctx.author.display_avatar.url)
            embed.add_field(name='Created', value=discord.utils.format_dt(check['time'], style='R'))
            embed.add_field(name='Fake Permissions', value=f"```{desc}```", inline=False)
            await ctx.send(embed=embed)
        else:
            return await util.send_error(ctx, f"{arg.mention} has no fake permissions")

    @fakeperms.command(
        aliases = ['list', 'all'],
        description = 'View all the fake permissions in your guild',
        brief = 'None',
        usage = 'administrator',
        help = '```Example: fakeperms view```'
    )
    @commands.has_permissions(administrator=True)
    async def view(self, ctx):
        check = await self.fakeperms.find_one({"guild_id": ctx.guild.id})
        if check:
            check_existing = self.fakeperms.find({"guild_id": ctx.guild.id})
            objects = []
            permissions = []
            for thing in await check_existing.to_list(length=100):
                obj = thing['object']
                perm = thing['fakeperms']
                try:
                    get_arg = ctx.guild.get_role(thing['object'])
                    objects.append(str(get_arg.mention))
                except:
                    pass
                    get_arg= ctx.guild.get_member(thing['object'])
                    objects.append(str(get_arg.mention))
                permissions.append(perm)
           # permissions = ", ".join(permissions[0])
            #print(permissions)
            response = [f"{objects}: ``{permissions[0:]}``" for objects, permissions in zip(objects, permissions)]
            rows = []
            content = discord.Embed(description="", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
            content.set_author(name=f"Fake permissions in {ctx.guild.name}", icon_url=ctx.guild.icon.url)
            content.set_footer(text=f"{ctx.prefix}fakeperms info [member or role] for a more detailed look.")
            for count, i in enumerate(response, start=1):
                rows.append(f"**{count}.)** {i}")
            await util.send_as_page(ctx, content, rows)
        else:
            return await util.send_error(ctx, f"This guild has no fake permissions")

    @fakeperms.command(
        description = 'View all the fake permission options',
        brief = 'None',
        usage = 'administrator',
        help = '```Example: fakeperms options```'
    )
    @commands.has_permissions(administrator=True)
    async def options(self, ctx):
        permissions = ['ban_members', 'kick_members', 'administrator', 'manage_roles', 'manage_channels', 'moderate_members', 'manage_nicknames', 'manage_messages']
        flagged="\n".join(flag for flag in permissions)
        return await ctx.send(embed=discord.Embed(title=f"{self.urgentmoji} Fake Permissions", description=f"```{flagged}```", color=self.urgecolor))





            


async def setup(bot):
    await bot.add_cog(fperms(bot))