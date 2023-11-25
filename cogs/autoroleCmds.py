import discord, motor, asyncio, Core.utils as util, Core.confirm as cop_is_gae
from discord.ext import commands, tasks
from typing import List
import discord.ui
from colorama import Fore as f
from Core import utils as util

class autoRolE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db['autorole']
        self.cache = {}
        self.cacheAutoroles.start()

    @tasks.loop(minutes=60)
    async def cacheAutoroles(self):
        getAutoroles = self.db.find({})
        guild_ids = []
        autoroles = []
        for i in await getAutoroles.to_list(length=99999):
            get_guilds = i['guild_id']
            get_autoroles = i['autoroles']
            guild_ids.append(get_guilds)
            autoroles.append(get_autoroles)
        self.cache = {guild_ids: {'autoroles': autoroles} for (guild_ids, autoroles) in zip(guild_ids, autoroles)}
        print(f"{f.LIGHTRED_EX}[{f.RESET}{f.BLUE}Autoroles CACHED{f.RESET}{f.LIGHTRED_EX}]{f.RESET} {f.GREEN}->{f.RESET} {f.LIGHTGREEN_EX}{self.cache}{f.RESET}")

    @cacheAutoroles.before_loop
    async def before_cacheAutoroles(self):
        await self.bot.wait_until_ready()

    @commands.group(
        aliases = ['auto'],
        usage = 'manage_roles',
        description = 'Set a role that users will automatically be added to upon joining',
        brief = 'role',
        help = "```Syntax: autorole [subcommand] <arg>\nExample: autorole add @Users```"

    )
    async def autorole(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Command: autorole", description="Set a role that users will automatically be added to upon joining.\n```Syntax: autorole [subcommand] <arg>\nExample: autorole add @Users```", color = discord.Color.blurple())
                embed.set_author(name="autorole help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('autorole').walk_commands()])} ・ autorole")
                return await ctx.send(embed=embed)
        except Exception as e:
            print(e)

    @autorole.command(
        name='add',
        usage = 'manage_roles',
        description = 'Set a role that users will automatically be added to upon joining',
        brief = 'role',
        help = "```Syntax: autorole add [role]\nExample: autorole add @Users```"
        )
    @commands.has_permissions(manage_roles=True)
    async def autorole_add(self, ctx, role: discord.Role):
            check = await self.db.count_documents({ "guild_id": ctx.guild.id })
            if check:
                data = await self.db.find_one({ "guild_id": ctx.guild.id })
                role_list = data['autoroles']
                if len(role_list) > 2:
                    return await util.send_blurple(ctx, "Each server can only have ``2`` autorole's set.")
                if role.id in role_list:
                    return await util.send_error(ctx, f"{role.mention} is already an autorole!")
                else:
                    await self.db.update_one({"guild_id": ctx.guild.id}, {"$push": {"autoroles": role.id}})
                    self.cacheAutoroles.restart()
                    return await util.send_blurple(ctx, f"{role.mention} will now be roled to new members who join.")
            else:
                msgsend = await util.send_blurple(ctx, 'Setting up...')
                await asyncio.sleep(1.2)
                await self.db.insert_one({
                "guild_id": ctx.guild.id,
                "autoroles": [role.id]
        })
                self.cacheAutoroles.restart()
                return await msgsend.edit(embed=await util.edit_blurple(ctx, f"{role.mention} will now be roled to new members who join."))

    @autorole.command(
        name='remove',
        usage = 'manage_roles',
        description = 'Remove a current existing autorole',
        brief = 'role',
        help = "```Syntax: autorole remove [role]\nExample: autorole remove @Users```"
        )
    @commands.has_permissions(manage_roles=True)
    async def autorole_remove(self, ctx, role: discord.Role):
        data = await self.db.find_one({ "guild_id": ctx.guild.id })
        role_list = data['autoroles']
        if role.id in role_list:
            await self.db.update_one({"guild_id": ctx.guild.id}, {"$pull": {"autoroles": role.id}})
            self.cacheAutoroles.restart()
            return await util.send_blurple(ctx, f"{role.mention} has been removed and no longer will be given to members who join")
        else:
            return await util.send_blurple(ctx, f"{role.mention} is not an existing autorole")


    @autorole.command(
        name='clear',
        usage = 'manage_roles',
        description = 'Clear all existing autoroles in your server',
        brief = 'None',
        help = "```Syntax: autorole clear\nExample: autorole clear```"
        )
    @commands.has_permissions(manage_roles=True)
    async def autorole_clear(self, ctx):
        check = await self.db.count_documents({ "guild_id": ctx.guild.id })
        if check:
            yes = discord.Embed(description=f"{ctx.author.mention}: **Are you sure you want to clear all autoroles in your server?**")
            msg = await ctx.send(embed=yes)
            async def confirm():
                await self.db.delete_one({ "guild_id": ctx.guild.id })
                await msg.edit(view=None, embed=await util.edit_blurple(ctx, "All autoroles have been removed."))

            async def cancel():
                await msg.edit(view=None, embed=await util.edit_blurple(ctx, "Process cancelled"))
                pass

            confirmed:bool = await cop_is_gae.confirm(self, ctx, msg)
            if confirmed:
                await confirm()
                self.cacheAutoroles.restart()
            else:
                await cancel()


    @commands.command(
        name='autoroles',
        usage = 'manage_roles',
        description = 'View all the currently existing autoroles',
        brief = 'None',
        help = "```Syntax: autorole view\nExample: autorole view```"
        )
    @commands.has_permissions(manage_roles=True)
    async def autorole_autoroles(self, ctx):
        check = await self.db.count_documents({ "guild_id": ctx.guild.id })
        if check:
            data = await self.db.find_one({ "guild_id": ctx.guild.id })
            results = data['autoroles']
            if len(results) <= 0:
                return await util.send_error(ctx, f"This server does not have any autoroles.")
            rows = []
            content = discord.Embed(description="")
            for count, i in enumerate(results, start=1):
                role = ctx.guild.get_role(i)
                rows.append(f"``{count})`` {role.mention} - ``{role.id}`` ")
            await util.send_as_pages(ctx, content, rows)

    @autorole.command(
        name='view',
        usage = 'manage_roles',
        description = 'View all the currently existing autoroles',
        brief = 'None',
        help = "```Syntax: autorole view\nExample: autorole view```"
        )
    @commands.has_permissions(manage_roles=True)
    async def autorole_list(self, ctx):
        check = await self.db.count_documents({ "guild_id": ctx.guild.id })
        if check:
            data = await self.db.find_one({ "guild_id": ctx.guild.id })
            results = data['autoroles']
            if len(results) <= 0:
                return await util.send_error(ctx, "This server does not have any autoroles.")
            rows = []
            content = discord.Embed(description="")
            for count, i in enumerate(results, start=1):
                role = ctx.guild.get_role(i)
                rows.append(f"``{count})`` {role.mention} - ``{role.id}`` ")
            await util.send_as_pages(ctx, content, rows)


    @autorole.command(
        name='setup',
        usage = 'manage_roles',
        description = 'Setup the autorole module',
        brief = 'None',
        help = "```Syntax: autorole setup\nExample: autorole setup```"
        )
    @commands.has_permissions(manage_roles=True)
    async def autorole_setup(self, ctx):
        check = await self.db.find_one({ "guild_id": ctx.guild.id })
        if not check:
            return await util.send_blurple(ctx, f"This server does not have any autoroles.")
        else:
            msgsend = await util.send_blurple(ctx, "Setting up...")
            await asyncio.sleep(1.1)
            await msgsend.edit(embed=await util.edit_blurple(ctx, "Reviewing.."))

            await self.db.insert_one({
            "guild_id": ctx.guild.id,
            "autoroles": []
    })
            self.cacheAutoroles.restart()
            return await msgsend.edit(embed=await util.edit_blurple(ctx, "Congrats, you can now add autoroles to your server!"))

    @commands.Cog.listener("on_member_join")
    async def autorole_events(self, member):
        try:
            check = self.cache[member.guild.id]
        except KeyError:
            return
        data = self.cache[member.guild.id]
        results = data['autoroles']
        for i in results:
            role = member.guild.get_role(i)
            if role is None:
                await self.db.update_one({ "guild_id": member.guild.id }, { "$pull": { "autoroles": i }})
                self.cacheAutoroles.restart()
            if role.permissions.ban_members or role.permissions.kick_members or role.permissions.administrator or role.permissions.manage_channels or role.permissions.manage_webhooks or role.permissions.manage_roles or role.permissions.mention_everyone:
                await member.guild.owner.send(f"The autorole **{role.name}** - ``{role.id}`` Had admin permissions therefore, i've **removed** the autorole from your guild's autoroles.")
                await self.db.update_one({ "guild_id": member.guild.id }, { "$pull": { "autoroles": role.id }})
            else:
                await asyncio.sleep(1)
                await member.add_roles(role, reason='Autorole')

async def setup(bot):
    await bot.add_cog(autoRolE(bot))