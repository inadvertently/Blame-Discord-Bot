import discord
from discord.ext import commands, tasks
import Core.utils as utils
from Core.utils import get_theme

class boostevents(commands.Cog):
    def __init__(self, client):
        self.bot = client
        self.db = self.bot.db['boosters']


    @commands.group(
        aliases = ['boostmessage', 'booster', 'boost'],
        usage = 'administrator',
        description = 'Send a custom message/role that will be sent/given when a member boosts the server',
        brief = 'subcommand',
        help = "```Syntax;: boostmsg <subcommand>\nExample: boostmsg channel #boosts```" 
    )
    async def boostmsg(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="Command: boostmsg", description="Send a custom message to a specifiec channel when a member boosts ther server\n```Syntax;: boostmsg <subcommand>\nExample: boostmsg channel #boosts```", color = discord.Color.blurple())
            embed.set_author(name="boostmsg help", icon_url=ctx.me.avatar.url)
            embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('boostmsg').walk_commands()])} ・ boostmsg")
            return await ctx.send(embed=embed)
    
    @boostmsg.command(
        aliases = ['msg'],
        usage = 'administrator',
        description = 'Set a custom message for when someone boosts the server',
        brief = 'message',
        help = "```Syntax: boostmsg message [message]\nExample: boostmsg message thanks for boosting {user}```" 
    )
    @commands.has_permissions(administrator=True)
    async def message(self, ctx, *, message):
        check = await self.db.find_one({'guild_id': ctx.guild.id})
        if not check:
            return await utils.send_issue(ctx, f"You must enable this module first using, ``{ctx.prefix}boostmsg enable``")
        else:
            if message.startswith("(embed)"):
                params = message.replace('(embed)', '')
                params = await utils.test_vars(ctx, ctx.author, params)
                em = await utils.to_embed(ctx, params=message)
                msg = await utils.to_content(ctx, params=message)
                try:
                    await ctx.send(content=msg, embed=em)
                except Exception as e:
                    return await ctx.send(f"```{e}```")
                await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "message": str(message)}})
                return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention}: Your **boost message** has been **set** to:\n```{message}```", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
            if message.startswith("{embed}"):
                params = message.replace('{embed}', '')
                params = await utils.test_vars(ctx, ctx.author, params)
                em = await utils.bleed_embed(ctx, params=message)
                msg = await utils.bleed_content(ctx, params=message)
                try:
                    await ctx.send(content=msg, embed=em)
                except Exception as e:
                    return await ctx.send(f"```{e}```")
                await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "message": str(message)}})
                return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention}: Your **boost message** has been **set** to:\n```{message}```", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
            if not message.startswith("(embed)") or not message.startswith("{embed}"):
                message = await utils.test_vars(ctx, ctx.author, message)
                await ctx.send(message)
                await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "message": str(message)}})
                return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention}: Your **boost message** has been **set** to:\n```{message}```", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))




    @boostmsg.command(
        aliases = ['chan', 'chanel'],
        usage = 'administrator',
        description = 'Set the boost channel for when someone boosts',
        brief = 'message',
        help = "```Syntax: boostmsg channel [channel]\nExample: boostmsg channel #boosts```" 
    )
    @commands.has_permissions(administrator=True)
    async def channel(self, ctx, channel: discord.TextChannel):
        check = await self.db.find_one({'guild_id': ctx.guild.id})
        if not check:
            return await utils.send_issue(ctx, f"You must enable this module first using, ``{ctx.prefix}boostmsg enable``")
        else:
            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "channel": channel.id}})
            return await utils.send_blurple(ctx, f"Boostmsg notifications will now be send in <#{channel.id}>")
    
    @boostmsg.command(
        usage = 'administrator',
        description = 'Set a role that users will be given when they boost',
        brief = 'role',
        help = "```Syntax: boostmsg role [role]\nExample: boostmsg role @pic perms```" 
    )
    @commands.has_permissions(administrator=True)
    async def role(self, ctx, role: discord.Role):
        check = await self.db.find_one({'guild_id': ctx.guild.id})
        if not check:
            return await utils.send_issue(ctx, f"You must enable this module first using, ``{ctx.prefix}boostmsg enable``")
        else:
            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "role": role.id}})
            return await utils.send_blurple(ctx, f"{role.mention} will now be given to members when they boost!")

    @boostmsg.command(
        aliases = ['on'],
        usage = 'administrator',
        description = 'Enable the boostmsg module',
        brief = 'None',
        help = "```Example: boostmsg enable```" 
    )
    @commands.has_permissions(administrator=True)    
    async def enable(self, ctx):
        check = await self.db.find_one({'guild_id': ctx.guild.id})
        if not check:
            await self.db.insert_one({
                'guild_id': ctx.guild.id,
                'role': None,
                'channel': None,
                'message': None,
                'status': 'Enabled'
            })
            return await utils.send_blurple(ctx, f"The boostmsg module is now enabled! View the rest of it's commands with ``{ctx.prefix}help boostmsg``!")
        else:
            return await utils.send_issue(ctx, f"The boostmsg module is already enabled! View the rest of it's commands with ``{ctx.prefix}help boostmsg``!")

    @boostmsg.command(
        aliases = ['off'],
        usage = 'administrator',
        description = 'Disable the boostmsg module',
        brief = 'None',
        help = "```Example: boostmsg disable```" 
    )
    @commands.has_permissions(administrator=True)    
    async def disable(self, ctx):
        check = await self.db.find_one({'guild_id': ctx.guild.id})
        if not check:
            return await utils.send_error(ctx, f"The boostmsg module is not enabled in this server!")
        else:
            await self.db.delete_one({'guild_id': ctx.guild.id})
            return await utils.send_issue(ctx, f"The boostmsg module has now been disabled in this server.")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        #roles = [role.id for role in after.roles if role not in before.roles]
        try:
            if before.guild.premium_subscriber_role not in before.roles and after.guild.premium_subscriber_role in after.roles:
                check = await self.db.find_one({'guild_id': before.guild.id})
                if not check:
                    return
                else:
                    chan = check['channel']
                    message = check['message']
                    rol = check['role']
                    channel=self.bot.get_channel(chan)
                    role = before.guild.get_role(rol)
                    if not channel or channel is None and after.system_channel:
                        channel = after.system_channel.id
                    if not role:
                        pass
                    if message.startswith("(embed)"):
                        params = message.replace('(embed)', '')
                        params = await utils.welcome_vars(user=after, params=params)
                        em = await utils.to_embed(after, params=params)
                        msg = await utils.to_content(after, params=message)
                        try:
                            await channel.send(content=msg, embed=em)
                            await after.add_roles(role, reason="Boost role")
                        except Exception as e:
                            print(e)

                    if message.startswith("{embed}"):
                        params = message.replace('{embed}', '')
                        params = await utils.welcome_vars(user=after, params=params)
                        em = await utils.bleed_embed(after, params=params)
                        msg = await utils.bleed_content(after, params=message)
                        try:
                            await channel.send(content=msg, embed=em)
                            await after.add_roles(role, reason="Boost role")
                        except Exception as e:
                            print(e)

                    if not message.startswith("(embed)") or not message.startswith("{embed}"):
                        message = await utils.welcome_vars(user=after, params=message)
                        await channel.send(message)
                        await after.add_roles(role, reason="Boost role")
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(boostevents(bot))

