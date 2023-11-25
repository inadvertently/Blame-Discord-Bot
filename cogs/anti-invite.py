from distutils.log import error
import discord, aiohttp, re, os, datetime, logging,asyncio, humanfriendly, motor.motor_asyncio, Core.help as _init, db.database as connections, Core.confirm as cop_is_gae
from discord.ext import commands
from discord import Status
from datetime import timedelta
from colorama import Fore as f
import Core.help as util
import Core.utils as utils
from Core.utils import get_theme
    
class anti_inVe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db["anti-inv"]

    @commands.group(
        aliases = ['antiinv', 'anti-inv', 'filter'],
        name='anti-invite', 
        usage = 'Manage_messages',
        description="Filter invites from being set in your servers channels.", 
        brief = "group, subcommand, argument[Optional]",
        help = "```Syntax: anti-invite [group] [subcommand] <argument[Optional]>```"
        )
    async def anti_invite(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Command: anti-invite", description="Filter invites from being set in your servers channels.\n```Syntax: anti-invite [group] [subcommand] <argument[Optional]>```", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                embed.set_author(name="Anti-invite help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('anti-invite').walk_commands()])} ・ Anti-invite")
                return await ctx.send(embed=embed)
        except Exception as e:
            print(e)


    @anti_invite.group(
        description = "Whitelist a channel so the bot won't filter invites inside of it.",
        usage = "Manage_messages",
        brief = "channel",
        help = "```Syntax: anti-invite whitelist channel [channel]\nExample: anti-invite whitelist channel #partnerships```"
    )
    async def whitelist(self, ctx):
        if ctx.invoked_subcommand is None:
            await utils.send_error(ctx, "Improper command passed. Maybe you meant ``anti-invite whitelist channel``?")

    @whitelist.command(
        description = "Whitelist a channel so the bot won't filter invites inside of it.",
        usage = "Manage_messages",
        brief = "channel",
        help = "```Syntax: anti-invite whitelist channel [channel]\nExample: anti-invite whitelist channel #partnerships```"
    )
    @commands.has_permissions(manage_messages=True)
    async def channel(self, ctx, channel:discord.TextChannel=None):
        async with ctx.typing():
            try:
                check = await self.db.find_one({"guild_id": ctx.guild.id})
                if not check and channel == None:
                    await utils.send_command_help(ctx)
                if not check and channel:
                    await self.db.insert_one({
                        "guild_id": ctx.guild.id,
                        "anti-inv": None,
                        "time": None,
                        "author": None,
                        "whitelisted": []
                    })
                    await asyncio.sleep(1)
                    await self.db.update_one({"guild_id": ctx.guild.id}, {"$set": {"anti-inv": "Enabled"}})
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$push": { "whitelisted": channel.id}})
                    final = discord.Embed(description=f"<:check:921544057312915498> {channel.mention} **is now whitelisted and will no longer be monitored for invites**", timestamp=ctx.message.created_at, color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                    final.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
                    final.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
                    return await ctx.send(embed=final)
                if check and not channel:
                    await utils.send_command_help(ctx)
                if check and channel:
                    find = await self.db.find_one({"guild_id": ctx.guild.id})
                    data = find["whitelisted"]
                    if channel.id in data:
                        await utils.send_issue(ctx, f"{channel.mention} is already a ``whitelisted channel`` in this server.")
                    else:
                        await self.db.update_one({ "guild_id": ctx.guild.id }, { "$push": { "whitelisted": channel.id}})
                        final = discord.Embed(description=f"<:check:921544057312915498> {channel.mention} **is now whitelisted and will no longer be monitored for invites**", timestamp=ctx.message.created_at, color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                        final.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
                        final.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
                        return await ctx.send(embed=final)

            except Exception as e:
                pass
    
    @anti_invite.command(
        aliases = ['whl'],
        usage = "Manage_messages",
        description = "View the anti-invite whitelisted channels within you server",
        brief = "None",
        help = "```Example: anti-invite whitelisted```"
    )
    @commands.has_permissions(manage_messages=True)
    async def whitelisted(self, ctx):     
        try:
            oopi = await self.db.find_one({"guild_id": ctx.guild.id})
            oop = oopi['anti-inv']    
            if "Enabled" in oop:
                dataa = await self.db.find_one({ "guild_id": ctx.guild.id })
                data = dataa['whitelisted']
                embed = discord.Embed(title=f"Whitelisted channels <a:5864blurplesearch:921796451120590899>", description="", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                for i in data:
                    embed.description += f"<#{(i)}> - ``{i}\n``"
                await ctx.send(embed=embed)

        except:
            await utils.send_error(ctx, 'This module has not been enabled in this server.')
            pass


    @anti_invite.group(
        usage = "Manage_message",
        description = "Unwhitelist certain channels within the anti-invite module",
        brief = "channel",
        help = "```Example: anti-invite unwhitelist channel [channel]```",
        aliases = ["unwhl"]
    )
    async def unwhitelist(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                await utils.send_error(ctx, "Improper command passed. Maybe you meant ``anti-invite unwhitelist channel``?")
        except Exception as e:
            print(e)


    @unwhitelist.group(
        name = "channel",
        brief = "channel",
        help = "```Syntax: anti-invite unwhitelist channel [channel]\nExample: anti-invite unwhitelist channel #general```",
        description = "Unwhitelist a previously whitelisted channel"
    )
    async def channels(self, ctx, channel:discord.TextChannel):
        async with ctx.typing():
            check = await self.db.find_one({"guild_id": ctx.guild.id})
            if not check:
                await utils.send_command_help(ctx)
            if check:
                find = await self.db.find_one({"guild_id": ctx.guild.id})
                data = find["whitelisted"]
                if channel.id in data:
                    await utils.send_blurple(ctx, f"{channel.mention} has been unwhitelisted and will now be ``monitored`` for invites.")
                    return await self.db.update_one({ "guild_id": ctx.guild.id }, { "$pull": { "whitelisted": channel.id}})
                else:
                    return await utils.send_error(ctx, f"{channel.mention} is not a ``whitelisted`` channel in this server")

    @anti_invite.command(
        usage = "Manage_message",
        description = "Disable the module",
        brief = "None",
        help = "```Example: anti-invite disable```",
        aliases = ["off"]
    )
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx):
        try:
            oop = await self.db.find_one({"guild_id": ctx.guild.id})
            if oop:
                msg = await utils.send_question(ctx, "Are you sure you'd like to disable ``anti-invite`` for this serer?")
                async def confirm():
                    await self.db.delete_many({ "guild_id": ctx.guild.id })
                    await msg.edit(view=None, embed=discord.Embed(description="<:check:1027703035054526475> **Disabled** ``anti-invite`` for this server.", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                async def cancel():
                    await msg.edit(view=None, embed=discord.Embed(description="<:bad:1028153588989571094> **Cancelled.**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                    pass
                confirmed:bool = await cop_is_gae.confirm(self, ctx, msg)
                if confirmed:
                    await confirm()
                else:
                    await cancel()
            else:
                return await utils.send_error(ctx, 'The anti-invite is not enabled in this server.' )
        except:
            pass

    @anti_invite.command(
        aliases = ['enable', 'on'],
        usage = "Manage_message",
        description = "Enable the module so it can filter discord invites from being sent in your chats",
        brief = "None",
        help = "```Example: anti-invite enable```",
    )
    async def enabled(self, ctx):
        try:
            check = await self.db.find_one({ "guild_id": ctx.guild.id})
            if check:
                return await utils.send_error(ctx, 'The anti-invite is already enabled in this server.' )
            else:
                await utils.send_blurple(ctx, 'Anti-invite is now ``enabled`` in this server.')
                return await self.db.insert_one({
                    "guild_id": ctx.guild.id,
                    "anti-inv": "Enabled",
                    "time": None,
                    "author": None,
                    "whitelisted": []
                })
        except: pass; return


    async def invite_find(self, message):
        DISCORD_INVITE = r'(?:https?://)?(?:www.:?)?discord(?:(?:app)?.com/invite|.gg)/?[a-zA-Z0-9]+/?'
        dsg=r'(https|http)://(dsc.gg|discord.gg|discord.io|dsc.lol)/?[\S]+/?'
        r=re.compile(DISCORD_INVITE)
        rr=re.compile(dsg)
        invites=r.findall(message)
        invs=rr.findall(message)
        if len(invites) >= 1 or len(invs) >= 1:
            return True
        else:
            return False

    @commands.Cog.listener()
    async def on_message(self, message):
        #if message.guild.id == 
        if message.author == self.bot.user:
            return
        #if "discord.gg" in message.content.lower() or "discord.com/" in message.content.lower() or "discordapp.com/invite" in message.content.lower():
        if await self.invite_find(message.content.lower()):
            try:
                guild =  message.guild
                #role = discord.utils.get(guild.roles, name="amuted")
                oopi = await self.db.find_one({"guild_id": guild.id})
                oop = oopi['anti-inv']
                whitelistedd = await self.db.find_one({ "guild_id": guild.id })
                whitelisted = whitelistedd['whitelisted']
                if message.channel.id in whitelisted:
                    return
                if message.author.guild_permissions.manage_messages:
                    return
                if oop == "Enabled":
                    await message.delete()
                    time =  '1minute'
                    timeConvert = humanfriendly.parse_timespan(time)
                    await message.author.timeout(discord.utils.utcnow()+datetime.timedelta(seconds=timeConvert), reason="Sending invites while anti-invite is enabled")
                    try:
                        #await utils.send_issue(message.channel, "You've been muted for ``1 minute`` for sending ``invites`` in this channel.")
                        await message.channel.send(f"<:danger:921613173390475314> {message.author.mention}: You've been muted for **1 minute** for sending **invites** in this channel.", delete_after=10)
                    except Exception as e:
                        print(e); pass
                    #await message.author.add_roles(role)
            except Exception as e:
                print(e); pass; return
        else:
            return

    

async def setup(bot):
    await bot.add_cog(anti_inVe(bot))