import discord, aiohttp, string, random
from discord import Webhook
from discord.ext import commands
import Core.utils as utils
from datetime import datetime
from Core.utils import get_theme


async def codeGen(size=6, chars=string.ascii_uppercase + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))

def strip_codeblock(content):
    if content.startswith('```') and content.endswith('```'):
        return content.strip('```')
    return content.strip('` \n')

class Flags(commands.FlagConverter, prefix='--', delimiter=' ', case_insensitive=True):
    @classmethod
    async def convert(cls, ctx, argument: str):
        argument = strip_codeblock(argument).replace(' —', ' --')
        return await super().convert(ctx, argument)
    channel: discord.TextChannel =None
    name: str 
    avatar: str=None

class webhookcog(commands.Cog):
    def __init__(self, client):
        self.bot = client
        self.webhooks = self.bot.db['webhooks']
        #self.color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)

    @commands.group(aliases =['webhooks', 'w'])
    async def webhook(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Command: webhook", description="Control webhooks through the bot\n```Syntax: webhook [subcommand] <argument>\nExample: webhook create --name hi --channel #general --avatar URL```", color = discord.Color.blurple())
                embed.set_author(name="webhook help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('webhook').walk_commands()])} ・ webhook")
                return await ctx.send(embed=embed)
        except Exception as e:
            print(e)

    @webhook.command(
    aliases =['add', 'make'],
    usage = "Manage_webhooks",
    description = "Create a webhook through the bot",
    brief = "subcommand, flags",
    help = "```Syntax: webhook create --name [name] --channel [channel] --avatar [URL/IMG]\nExample: webhook create --name hi --channel #general --avatar URL```"
    )
    @commands.has_permissions(manage_webhooks=True)
    async def create(self, ctx, *, flags: Flags):
        async with ctx.typing():
            if flags.channel==None:
                flags.channel = ctx.channel
            if flags.name == None:
                return await utils.send_command_help(ctx)
            if flags.avatar and flags.avatar.startswith('https://'):
                async with aiohttp.ClientSession() as session:
                    async with session.get(flags.avatar) as response:
                        flags.avatar = await response.read()
            webhook = await flags.channel.create_webhook(name=flags.name, avatar=flags.avatar, reason=f"Webhook created by {ctx.author}")
            code = await codeGen()
            await utils.send_blurple(ctx, f"Created **webhook** with code **``{code}``**. This is the code you'll need to **edit/send** with the webhook")
            time = datetime.now()
            await self.webhooks.insert_one({
                "guild_id": ctx.guild.id,
                "code": str(code),
                "url": str(webhook.url),
                "channel": str(flags.channel.mention),
                "time": time
            })

    @webhook.command(
    aliases =['del', 'remove'],
    usage = "Manage_webhooks",
    description = "Delete a webhook through the bot",
    brief = "code",
    help = "```Syntax: webhook delete [code]\nExample: webhook delete BalVBA```"

    )
    @commands.has_permissions(manage_webhooks=True)
    async def delete(self, ctx, code:str):
        check = await self.webhooks.find_one({"guild_id": ctx.guild.id, "code": code})
        if check:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(f'{check["url"]}', session=session)
                await webhook.delete(reason=f"Deleted by {ctx.author}")
            await utils.send_blurple(ctx, f"Deleted webhook with code ``{code}``")
            await self.webhooks.delete_one({"guild_id": ctx.guild.id, "code": code})
        else:
            return await utils.send_error(ctx, f"Invalid webhook with code **``{code}``")

    @webhook.command(
    aliases =['post'],
    usage = "Manage_webhooks",
    description = "Send a message or embed to a webhook via the bot",
    brief = "code, message",
    help = "```Syntax: webhook send [code] [message]\nExample: webhook send BalVBA (embed)(title: hi)```"

    )
    @commands.has_permissions(manage_webhooks=True)
    async def send(self, ctx, code, *, message):
        check = await self.webhooks.find_one({ "guild_id": ctx.guild.id, "code": str(code)})
        if not check:
            return await utils.send_error(ctx, f"Invalid webhook with code ``{code}``")
        else:
            if message.startswith("(embed)"):
                message = message.replace('(embed)', '')
               #message = await utils.test_vars(ctx, user, params=message)
                em = await utils.to_embed(ctx, params=message)
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(f'{check["url"]}', session=session)
                    try:
                        await webhook.send(embed=em)
                    except Exception as e:
                        return await ctx.send(f"```{e}```")
                return await ctx.send(embed=discord.Embed(description=f"```{message}```\n<:check:921544057312915498> **Sent**", color=0x43B581))
            elif not message.startswith("(embed)"):
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(f'{check["url"]}', session=session)
                    try:
                        await webhook.send(f'{message}')
                    except Exception as e:
                        return await ctx.send(f"```{e}```")
                return await ctx.send(embed=discord.Embed(description=f"```{message}```\n<:check:921544057312915498> **Sent**", color=0x43B581))

    @webhook.command(
    aliases =['list', 'all'],
    usage = "Manage_webhooks",
    description = "View the servers existing webhooks",
    brief = "None",
    help = "```Example: webhook view```"

    )
    @commands.has_permissions(manage_webhooks=True)
    async def view(self, ctx):
        check = await self.webhooks.find_one({"guild_id": ctx.guild.id})
        if check:
            check_existing = self.webhooks.find({ "guild_id": ctx.guild.id})
            codes = []
            times = []
            channels = []
            for data in await check_existing.to_list(length=15):
                time = data['time']
                channel = data['channel']
                code = data['code']
                codes.append(code)
                times.append(time)
                channels.append(channel)
            resp = [f"``{codes}`` set for {channels} {discord.utils.format_dt(times, style='R')}" for codes, channels, times in zip(codes, channels, times)]
            rows= []
            content = discord.Embed(description ="", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
            content.set_author(name=f"Webhooks in {ctx.guild.name} ({ctx.guild.id})", icon_url=ctx.guild.icon.url)

            for count, i in enumerate(resp, start=1):
                rows.append(f"**{count}.)** {i}")
            #content.set_footer(text=f"")
            await utils.send_as_pages(ctx, content, rows)
        else:
            return await utils.send_error(ctx, f"I have no existing webhooks in this guild")



    @webhook.group(
    aliases =['e'],
    usage = "Manage_webhooks",
    description = "Edit existing webhooks through the bot",
    brief = "[subcommand] <argument>",
    help = "```Syntax: webhook edit [subcommand] <argument>\nExample: webhook edit name blame```"
        )
    async def edit(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Command: webhook edit", description="Edit existing webhooks through the bot\n```Syntax: webhook edit [subcommand] <argument>\nExample: webhook edit name blame```", color = discord.Color.blurple())
                embed.set_author(name="webhook edit help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('webhook').walk_commands()])} ・ webhook edit")
                return await ctx.send(embed=embed)
        except Exception as e:
            print(e)

    @edit.command(
    aliases =['n'],
    usage = "Manage_webhooks",
    description = "Edit an existing webhook name",
    brief = "code, name",
    help = "```Syntax: webhook edit name [code] [new_name]\nExample: webhook edit name BalVBA newname```"
        
    )
    @commands.has_permissions(manage_webhooks=True)
    async def name(self, ctx, code, *, name):
        check = await self.webhooks.find_one({ "guild_id": ctx.guild.id, "code": str(code)})
        if not check:
            return await utils.send_error(ctx, f"Invalid webhook with code ``{code}``")
        else:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(f'{check["url"]}', session=session)
                await webhook.edit(name=str(name))
            return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> Webhook with code: **{code}** has **changed its name** to: **{name}**", color=0x43B581))

    @edit.command(
    aliases =['av', 'pfp', 'icon'],
    usage = "Manage_webhooks",
    description = "Edit an existing webhook avatar",
    brief = "code, new_avatar",
    help = "```Syntax: webhook edit avatar [code] [new_avatar]\nExample: webhook edit avatar BalVBA https://newavatar.png```"

    )
    @commands.has_permissions(manage_webhooks=True)
    async def avatar(self, ctx, code, avatar=None):
        vaild_urls = ['https', 'http']
        check = await self.webhooks.find_one({ "guild_id": ctx.guild.id, "code": str(code)})
        zz = None
        if not check:
            return await utils.send_error(ctx, f"Invalid webhook with code ``{code}``")
        
        if ctx.message.attachments:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(ctx.message.attachments[0].url) as response:
                    avatar = await response.read() 
                    zz = ctx.message.attachments[0].url
        if str(avatar).lower().startswith(tuple(vaild_urls)):
            async with aiohttp.ClientSession() as sess:
                async with sess.get(avatar) as response:
                    avatar = await response.read()
                    zz = avatar
        if avatar == None:
            return await utils.send_command_help(ctx)
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(f'{check["url"]}', session=session)
            await webhook.edit(avatar=avatar)
        return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> Webhook with code: **{code}** has **changed its avatar** to: ", color=0x43B581).set_image(url=zz))



async def setup(client): 
    await client.add_cog(webhookcog(client))
