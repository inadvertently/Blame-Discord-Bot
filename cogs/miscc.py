import discord, base64,re, difflib, arrow, io, aiofiles,unicodedata, os, aiohttp, humanize, datetime, pathlib, os, psutil, humanfriendly,sys, ast, inspect
from discord.ext import commands, tasks
from pytz import timezone
from Core import confirm
from Core import utils as util
import typing,tweepy
from typing import Union
import datetime
import random, re, asyncio
from itertools import chain
from discord import ui
from datetime import timedelta, datetime
import time, psutil, pkg_resources
from colorama import Fore as f
from Core.utils import get_theme
from Core import http, cash
import button_paginator as pg
from io import BytesIO
from PIL import Image
import xmltodict
from gtts import gTTS
from bs4 import BeautifulSoup
import urllib.parse
import Core.utils as utils


spotify_token = ""
spotify_token_expiry = 0.0

async def get_spotify_token() -> str:
    global spotify_token, spotify_token_expiry
    if spotify_token_expiry - 300 > time.time():
        print(f"using spotify token: {spotify_token[:41]}")
        return spotify_token
    async with aiohttp.ClientSession() as session:
        async with session.post("https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=aiohttp.BasicAuth(os.environ.get("SPOTIFY_CLIENT_ID"), os.environ.get("SPOTIFY_CLIENT_SECRET")),
        ) as r:
            spot = await r.json()
            spotify_token = spot["access_token"]
            spotify_token_expiry = time.time() + 3600
            print(f"updated spotify token: {spotify_token[:41]}")
            return spotify_token

async def get_info(link):
   is_true = "https?://open.spotify.com/(?P<type>album|playlist|track)/(?P<id>[a-zA-Z0-9]+)"
   get = re.search(is_true, link)
   if get:
      link = link.strip("https://open.spotify.com/track/")
      headers = {"Authorization": f"Bearer {await get_spotify_token()}"}
      base = f"https://api.spotify.com/v1/tracks/"
      async with aiohttp.ClientSession() as session:
         async with session.get(str(base+link), headers=headers) as scrape:
            results = await scrape.json()
            return results
   else:
      raise TypeError("error")

async def count_lines(path: str, filetype: str = '.py'):
    lines = 0
    for i in os.scandir(path):
        if i.is_file():
            if i.path.endswith(filetype):
                lines = len((await (await aiofiles.open(i.path, 'r')).read()).split("\n"))
        elif i.is_dir():
            lines += await count_lines(i.path, filetype)
    return lines


async def count_others(path: str, filetype: str = '.py', file_contains: str = 'def'):
    line_count = 0
    for i in os.scandir(path):
        if i.is_file():
            if i.path.endswith(filetype):
                line_count += sum(chain(
                    [len(line) for line in (await (await aiofiles.open(i.path, 'r')).read()).split("\n") if file_contains in line]
                ))
        elif i.is_dir():
            line_count += await count_others(i.path, filetype, file_contains)
    return line_count

devs = []
errorcol = 0xA90F25
urgecolor = 0xF3DD6C
checkmoji = "<:blurple_check:921544108252741723>"
xmoji = "<:yy_yno:921559254677200957>"
urgentmoji = "<:n_:921559211366838282>"

class test(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label='Invite Me 🔗', style=discord.ButtonStyle.blurple)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('https://discord.com/api/oauth2/authorize?client_id=776128410547126322&permissions=8&scope=bot', ephemeral=True)
        self.value = True
        self.stop()

    @discord.ui.button(label=" ✉️ Support", style=discord.ButtonStyle.blurple)
    async def support(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('https://blame.gg/discord', ephemeral=True)
        self.value = True
        self.stop()

class names(discord.ui.View):
    def __init__(self, ctx, bot, userr):
        super().__init__()
        self.ctx = ctx
        self.bot = bot
        self.userr = userr

    @discord.ui.button(label='📝 Name History', style=discord.ButtonStyle.blurple)
    async def namehist(self, interaction: discord.Interaction, button: discord.ui.Button):
        #await interaction.response.send_message("Name")
        await interaction.response.defer()
        await self.ctx.invoke(self.bot.get_command('namehistory'), user=self.userr)
        button.disabled = True
        await interaction.message.edit(view=self)
        #self.value = True
        #self.stop()
    @discord.ui.button(label='⏰ Last Seen', style=discord.ButtonStyle.blurple)
    async def lastseenn(self, interaction: discord.Interaction, button: discord.ui.Button):
        #await interaction.response.send_message("Name")
        await interaction.response.defer()
        await self.ctx.invoke(self.bot.get_command('lastseen'), user=self.userr)
        button.disabled = True
        await interaction.message.edit(view=self)


def num(number):
    return ("{:,}".format(number))

USER_FLAGS = {
    'staff': '<:staff:921574394084618330>',
    'partner': '<:BadgePartner:925624836993204235>',
    'hypesquad': '<a:HypeSquadGold:921590663026450512>',
    'bug_hunter': '<:BadgeBugHunter:925625840488816700>',
    'hypesquad_bravery': '<:badge_bravery:921544099981570091>',
    'hypesquad_brilliance': '<:badge_brilliance:921544101726392320>',
    'bug_hunter_level_2': '<:BadgeBugHunterLvl2:925644695479144478>',
    'hypesquad_balance': '<:badge_balance:921544098773614612>',
    'early_supporter': '<:badge_earlysupporter:921544103039230032>',
    'verified_bot_developer': '<:VerifiedBotDev:921574550293073962>',
    'verified_bot': '<:blurple_bot2:921812004715524157><:blurple_bot1:921812007798337546>',
    'premium_since': '<:Nitro:921559383970816080>',
    'discord_certified_moderator': '<:BadgeCertifiedMod:925643690750382121>'
}

USER_EMOJIS = {
    'staff': '<:staff:921574394084618330>',
    'partner': '<:BadgePartner:925624836993204235>',
    'hypesquad': '<a:HypeSquadGold:921590663026450512>',
    'bug_hunter_level_2': '<:BadgeBugHunterLvl2:925644695479144478>',
    'bug_hunter': '<:BadgeBugHunter:925625840488816700>',
    'hypesquad_bravery': '<:badge_bravery:921544099981570091>',
    'hypesquad_brilliance': '<:badge_brilliance:921544101726392320>',
    'hypesquad_balance': '<:badge_balance:921544098773614612>',
    'early_supporter': '<:badge_earlysupporter:921544103039230032>',
    'verified_bot_developer': '<:VerifiedBotDev:921574550293073962>',
    'verified_bot': '<:blurple_bot2:921812004715524157><:blurple_bot1:921812007798337546>',
    'premium_since': '<:Nitro:921559383970816080>', 
    'discord_certified_moderator': '<:BadgeCertifiedMod:925643690750382121>'
}

def get_user_badges(user: discord.Member, bot, fetched_user: discord.User = None):
    flags = dict(user.public_flags)

    user_flags = []
    for flag, text in USER_FLAGS.items():
        try:
            if flags[flag]:
                user_flags.append(f'{text}')
        except KeyError:
            continue

    if user.display_avatar.is_animated():
        if "<:BadgeNitro:925627225020194836> " not in user_flags:
            user_flags.append(f'<:BadgeNitro:925627225020194836> ')

    elif fetched_user and fetched_user.banner:
        if "<:BadgeNitro:925627225020194836> " not in user_flags:
            user_flags.append(f'<:BadgeNitro:925627225020194836> ')



    else:
        pass

    return ' '.join(user_flags) if user_flags else None


def get_user_emojis(user: discord.Member, bot, fetched_user: discord.User = None):
    flags = dict(user.public_flags)

    user_flags = []
    for flag, text in USER_EMOJIS.items():
        try:
            if flags[flag]:
                user_flags.append(f'{text}')
        except KeyError:
            continue

    if user.display_avatar.is_animated():
        if "<:BadgeNitro:925627225020194836> " not in user_flags:
            user_flags.append(f'<:BadgeNitro:925627225020194836> ')

    elif fetched_user and fetched_user.banner:
        if "<:BadgeNitro:925627225020194836> " not in user_flags:
            user_flags.append(f'<:BadgeNitro:925627225020194836> ')


    else:
        pass

    return ' '.join(user_flags) if user_flags else None

def generate_user_statuses(member: discord.Member):
    mobile = {
        discord.Status.online: '<:StatusMobile:925843264442097664>',
        discord.Status.idle: '<:StatusMobile:925843264442097664>',
        discord.Status.dnd: '<:StatusMobile:925843264442097664>',
        discord.Status.offline: '<:StatusMobile:925843264442097664>'
    }[member.mobile_status]
    desktop = {
        discord.Status.online: '<:dsk1:921613170802581514>',
        discord.Status.idle: '<:dsk1:921613170802581514>',
        discord.Status.dnd: '<:dsk1:921613170802581514>',
        discord.Status.offline: '<:dsk1:921613170802581514>'

    }[member.desktop_status]
    return f"\u200b{desktop}\u200b{mobile}"

def get_perms(permissions: discord.Permissions):
    if permissions.administrator:
        return ['Administrator']
    wanted_perms = dict({x for x in permissions if x[1] is True} - set(discord.Permissions(521942715969)))
    return [p.replace('_', ' ').replace('guild', 'server').title() for p in wanted_perms]

class miscc(commands.Cog):
    def __init__(self, client):
        self.bot = client
        #self.color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)
        self.NUM_TO_STORE = 3
        self.snipes = {}
        self.deleted_msgs = {}
        self.warn=""
        self.process = psutil.Process(os.getpid())
        self.edited_msgs = {}
        self.reactions = {}
        self.snipe_limit = self.NUM_TO_STORE
        self.db = self.bot.db['globalCommands']
        self.staff = self.bot.db['blameStaff']

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        ch_id = message.channel.id
        try:
            if not message.author.bot:
                if message.content:
                    if ch_id not in self.deleted_msgs:
                        self.deleted_msgs[ch_id] = []
                    self.deleted_msgs[ch_id].append(message)
                else:
                    if ch_id not in self.deleted_msgs:
                        self.deleted_msgs[ch_id] = []
                    self.deleted_msgs[ch_id].append(message)
                if len(self.deleted_msgs[ch_id]) > self.snipe_limit:
                    self.deleted_msgs[ch_id].pop(0)
        except:
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        channel = payload.channel_id
        if channel not in self.reactions:
            self.reactions[payload.guild_id] = {'user': [], 'time': [], 'emoji':[], 'url': [], 'channel': []}
        

        snipes = self.reactions[payload.guild_id]
        if payload.emoji.id == None:
            snipes['emoji'].insert(0, payload.emoji.name)
        else:
            snipes['emoji'].insert(0, payload.emoji.id)
        snipes['user'].insert(0, payload.user_id)
        snipes['time'].insert(0, datetime.now())
        snipes['url'].insert(0, payload.message_id)
        snipes['channel'].insert(0, payload.channel_id)
    
    @commands.hybrid_command(
        aliases=['rsnipe', 'rs', 'r', 'reactionsnipe'],
        description = 'See who secretley unreacted to messages',
        brief = "None"
        )
    async def snipereaction(self,ctx, limit=0):
        newlimit = 0
        #if limit > self.snipe_limit:
            #return await ctx.send(delete_after=5, embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"{self.warn} {ctx.author.mention}: **current snipe limit is {self.snipe_limit}**"))
        try:
            if limit == 0:
                newlimit == 1

            get = self.reactions[ctx.guild.id]
            emoji = self.bot.get_emoji(get['emoji'][int(limit)])
            if emoji == None:
                emoji = get['emoji'][int(limit)]

            user = self.bot.get_user(get['user'][int(limit)])
            embed = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
            embed.set_author(name=f"{user} unreacted", icon_url=user.display_avatar.url)
            try:
                a = await ctx.fetch_message(get['url'][int(limit)])
                embed.description=f"{emoji} - **[{a.content}](https://discordapp.com/channels/{ctx.guild.id}/{get['channel'][int(limit)]}/{get['url'][int(limit)]})** {discord.utils.format_dt(get['time'][int(limit)], style='R')}"
            except:
                pass
                embed.description=f"{emoji} - **[message](https://discordapp.com/channels/{ctx.guild.id}/{get['channel'][int(limit)]}/{get['url'][int(limit)]})** {discord.utils.format_dt(get['time'][int(limit)], style='R')}"
            embed.set_footer(text=f"reaction sniped")
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            await ctx.send(delete_after=5, embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"{self.warn} {ctx.author.mention}: **there is no reactions to snipe**"))
            


    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        ch_id = before.channel.id
        if not before.author.bot:
            if before.content and after.content:
                if ch_id not in self.edited_msgs:
                    self.edited_msgs[ch_id] = []
                self.edited_msgs[ch_id].append((before, after))
            else:
                if ch_id not in self.edited_msgs:
                    self.edited_msgs[ch_id] = []
                self.edited_msgs[ch_id].append((before, after))
            try:
                if len(self.edited_msgs[ch_id]) > self.snipe_limit:
                    self.edited_msgs[ch_id].pop(0)
            except:
                pass

    @commands.command(name="removesnipe", brief="int", aliases=["rms"], description="remove a snipe")
    @commands.has_permissions(manage_messages=True)
    async def removesnipe(self, ctx, snipe: int = 3):
        limit=snipe
        if limit > self.snipe_limit:
            return await ctx.send(delete_after=5, embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"{self.warn} {ctx.author.mention}: **current snipe limit is {self.snipe_limit}**"))
        try:
            snipe=snipe-1
            self.deleted_msgs[ctx.channel.id][snipe]="Snipe Has Been Removed"
            self.edited_msgs[ctx.channel.id][snipe]="Snipe Has Been Removed"
            await ctx.message.add_reaction("✅")
        except:
            await ctx.message.add_reaction("❎")

    @commands.hybrid_command(name="snipe",aliases=["s"],description="See recently deleted messages in the current channel",brief="int")
    async def snipe(self, ctx: commands.Context, limit: int = 1):
        if limit > self.snipe_limit:
            return await ctx.send(delete_after=5, embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"{self.warn} {ctx.author.mention}: **current snipe limit is {self.snipe_limit}**"))
        try:
            msgs: list[discord.Message] = self.deleted_msgs[ctx.channel.id][::-1][:limit]
            for msg in msgs:
                if msg == "Snipe Has Been Removed":
                    return await ctx.reply(delete_after=10, embed=discord.Embed(description=f"**{msg}**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                snipe_embed = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), timestamp = msg.created_at).set_author(name = msg.author, icon_url = msg.author.display_avatar).set_footer(text=f"{limit}/{len(self.deleted_msgs[ctx.channel.id])}")
                if msg.content:
                    snipe_embed.description=msg.content
                if msg.attachments:
                    snipe_embed.set_image(url=msg.attachments[0].proxy_url)
            await ctx.send(embed=snipe_embed)

        except:
            await ctx.send(delete_after=5, embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"{self.warn} {ctx.author.mention}: **there is nothing to snipe**"))

    @commands.hybrid_command(name="editsnipe",aliases=["es"],description="See recently edited messages in the current channel",brief="int")
    async def editsnipe(self, ctx: commands.Context, limit: int = 1):
        if limit > self.snipe_limit:
            return await ctx.send(delete_after=5, embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"{self.warn} {ctx.author.mention}: **current snipe limit is {self.snipe_limit}**"))
        try:
            msgs = self.edited_msgs[ctx.channel.id][::-1][:limit]
            for msg in msgs:
                if msg == "Snipe Has Been Removed":
                    return await ctx.reply(delete_after=10, embed=discord.Embed(description=f"**{msg}**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                editsnipe_embed = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), timestamp = msg[0].edited_at).set_author(name = msg[0].author, icon_url = msg[0].author.display_avatar).set_footer(text=f"{limit}/{len(self.edited_msgs[ctx.channel.id])}")
                if msg[0].content:
                    editsnipe_embed.description=msg[0].content
                if msg[0].attachments:
                    editsnipe_embed.set_image(url=msg[0].attachments[0].proxy_url)
            await ctx.send(embed=editsnipe_embed)

        except KeyError:
            await ctx.send(delete_after=5, embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"{self.warn} {ctx.author.mention}: **there is nothing to snipe**"))


    @commands.hybrid_command(name="quote", description="quote a message thru the bot", brief="message")
    async def quote(self, ctx, message=None):
        embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
        if not message:
            if ctx.message.reference:
                try: message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                except: return await util.send_error(ctx, f"I couldn't find a message under that ID")
                if message.content:
                    embed.description=message.content
                if message.attachments:
                    embed.set_image(url=message.attachments[0])
                embed.set_author(name=message.author, icon_url=message.author.display_avatar)
                embed.timestamp=message.created_at
                await message.reply(embed=embed)
        else:
            try:
                parts = [x for x in message.replace("/"," ").split() if len(x)]
                try: channel_id,message_id = [int(x) for x in parts[-2:]]
                except: pass
                channel = ctx.guild.get_channel(channel_id)
                if not channel: return await util.send_error(ctx, f"I couldn't find a channel under that ID")
                try: message = await channel.fetch_message(message_id)
                except: return await util.send_error(ctx, f"I couldn't find a message under that ID")
            except:
                try: message = await ctx.channel.fetch_message(message)
                except: return await util.send_error(ctx, f"I couldn't find a message under that ID")
            if message.content:
                embed.description=message.content
            if message.attachments:
                embed.set_image(url=message.attachments[0])
            embed.set_author(name=message.author, icon_url=message.author.display_avatar)
            embed.timestamp=message.created_at
            await message.reply(embed=embed)

    @commands.hybrid_command(
        aliases = ['shop', 'fs'],
        usage = "Send_messages",
        description = "View todays item shop",
        brief = "None",
        help = f"```Example: fortnite"
    )
    async def fortnite(self, ctx):
        embed = discord.Embed(title="Today's Shop", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), timestamp=ctx.message.created_at)
        embed.set_image(url=f"https://bot.fnbr.co/shop-image/fnbr-shop-{datetime.now().strftime('%d-%m-%Y').replace('0', '').replace('222', '2022')}.png?")
        await ctx.send(embed=embed)

    @commands.command(name='avatar', aliases=['av'], description="show a user's avatar", usage='Send Messages', help="```Example: ;av @cop#0001```", brief='member/id')
    async def avatar(self, ctx, member: Union[discord.Member, discord.User, str] = None):
        if isinstance(member, str):
            channel=ctx.channel
            mem=[]
            me=member
            members=[m.name.lower() for m in ctx.guild.members]
            closest=difflib.get_close_matches(me, members,n=1, cutoff=0)
            user=discord.utils.find(lambda m: m.name == closest[0], channel.guild.members)
            av=user.avatar or user.default_avatar
            await ctx.send(embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"[{user.name}'s avatar]({av})").set_image(url=av).set_footer(text=f"Requested by {ctx.author}"))
        else:
            if member is None:
                member = ctx.author
            if not member:
                member=self.bot.get_user(member)
            user=member
            av=user.avatar or user.default_avatar
            await ctx.send(embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"[{member.name}'s avatar]({av})").set_image(url=av).set_footer(text=f"Requested by {ctx.author}"))

    @commands.hybrid_command(name='serverav', aliases=['sav'], description="show a user's guild avatar", usage='Send Messages', help='```Example: ;sav @cop#0001```', brief='member/id')
    async def serverav(self, ctx, member:typing.Union[discord.Member]=None):
        if isinstance(member, str):
            channel=ctx.channel
            mem=[]
            me=member
            members=[m.name.lower() for m in ctx.guild.members]
            closest=difflib.get_close_matches(me, members,n=1, cutoff=0)
            memb=discord.utils.find(lambda m: m.name == closest[0], channel.guild.members)
            if memb.guild_avatar:
                pass
            else:
                return await util.send_error(ctx, f"member {memb.mention} doesn't have a server avatar")
            await ctx.send(embed=discord.Embed(description=f"[{memb.name}'s serveravatar]({memb.display_avatar.url})", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)).set_image(url=memb.display_avatar.url).set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url))
        else:
            member = member if member else ctx.author
            if member.guild_avatar:
                pass
            else:
                return await util.send_error(ctx, f"member {member.mention} doesn't have a server avatar")
            await ctx.send(embed=discord.Embed(description=f"[{member.name}'s serveravatar]({member.display_avatar.url})", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)).set_image(url=member.display_avatar.url).set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url))

    @commands.hybrid_command(name='banner', description="show a user's banner", usage='Send Messages', help="```Example: ;banner @cop#0001```", brief='member/id')
    async def banner(self, ctx, user:typing.Union[discord.Member, discord.User]=None):
        footer=f"Requested by {ctx.author}"
        user = user or ctx.author
        user = await self.bot.fetch_user(user.id)
        if user.banner:
            link=user.banner.with_size(512)
            embed=discord.Embed(description=f"[{user.name}'s banner]({link})", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
            embed.set_image(url=link)
            embed.set_footer(text=footer)
            await ctx.send(embed=embed)
        else:
            eembed=discord.Embed(description=f"***{user.mention} does not have a banner set***", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)).set_footer(text=footer)  
            await ctx.send(embed=eembed)

    @commands.hybrid_group(name='server', aliases=['serverinfo', 'si'], description="server info commands", usage='Send Messages')
    @commands.guild_only()
    async def server(self, ctx):
        if ctx.invoked_subcommand is None:
            infoemoji=self.bot.get_emoji(926308238322987058)
            guild=ctx.guild
            server_embed = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)).set_thumbnail(url=guild.icon)
            server_embed.title = f"{infoemoji} {guild.name}"
            last_boost = max(guild.members, key=lambda m: m.premium_since or guild.created_at)
            server_embed.description=f"Server Created {discord.utils.format_dt(guild.created_at, style='R')}"
            online_members = 0
            bot_member = 0
            bot_online = 0
            desc = ""
            for i in ctx.guild.features:
                desc +=f"{i}, "
            for member in guild.members:
                if member.bot:
                    bot_member += 1
                    if not member.status == discord.Status.offline:
                            bot_online += 1
                    continue
                if not member.status == discord.Status.offline:
                    online_members += 1
            user_string = "***Users:*** {:,} ({:,g}%)".format(
                    online_members,
                    round((online_members/(len(guild.members) - bot_member) * 100), 2)
            )
            b_string = "bot" if bot_member == 1 else "bots"
            user_string += "\n***Bots:*** {:,} ({:,g}%)".format(
                    bot_online,
                    round((bot_online/bot_member)*100, 2)
            )
            total_users="\n***Total:*** {:,}".format(len(guild.members))
            if guild.banner:
                banner=f"[Banner]({guild.banner})"
            else:
                banner=""
            if guild.splash:
                splash=f"[Splash]({guild.splash})"
            else:
                splash=""
            if guild.icon:
                icon=f"[Icon]({guild.icon})"
            else:
                icon=""
            bcounter=0
            for member in guild.members:
                if member.premium_since:
                    bcounter+=1
            total_count = len(guild.text_channels) + len(guild.voice_channels) + len(guild.categories)
            bcount="{}/{}".format(guild.premium_tier, guild.premium_subscription_count)
            #server_embed.add_field(name="Members", value="{:,}/{:,} online ({:.2f}%)\n{:,} {} ({}%)".format(online_members, len(guild.members), bot_percent), inline=True)
            server_embed.add_field(name="Owner", value=guild.owner.name+"#"+guild.owner.discriminator, inline=True)
            server_embed.add_field(name="Members", value=user_string+total_users, inline=True)
            server_embed.add_field(name="Info", value=f"**Verification: **{guild.verification_level}\n**Level:** {bcount}\n**Large:** {guild.large}", inline=True)
            server_embed.add_field(name="Design", value=f"{icon}\n{banner}\n{splash}", inline=True)
            chandesc = "**Categories:** {:,}\n**Text:** {:,}\n**Voice:** {:,} ".format(len(guild.text_channels), len(guild.voice_channels), len(guild.categories))
            server_embed.add_field(name=f"Channels({total_count})", value=chandesc, inline=True)
            server_embed.add_field(name="Counts", value=f"**Roles:** {str(len(guild.roles))}\n**Emojis:** {str(len(guild.emojis))}\n**Boosters:** {bcounter}", inline=True)
            server_embed.add_field(name="Features:", value=f"```{desc}```", inline=True)
            await ctx.send(embed=server_embed)
            

    @server.command(name="avatar", aliases=["icon", "a"], description="send the guild's current avatar")
    async def server_avatar(self, ctx):
        """ Get the current server icon """
        if not ctx.guild.icon:
            return await ctx.send(embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"this server does not have a avatar"))
        embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"[{ctx.guild.name}'s icon]({ctx.guild.icon})")
        embed.set_image(url=ctx.guild.icon)
        await ctx.send(embed=embed)

    @server.command(name="banner", aliases=['ban', 'b'], description="send the guild's current banner")
    async def server_banner(self, ctx):
        """ Get the current banner image """
        if not ctx.guild.banner:
            return await ctx.send(embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description="this server does not have a banner"))
        await ctx.send(embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"[{ctx.guild.name}'s banner]({ctx.guild.banner})").set_image(url=ctx.guild.banner))

    @server.command(name='splash', aliases=['invite', 'i', 's'], description="send the guild's current invite background")
    async def server_splash(self, ctx):
        guild=ctx.guild
        if not guild.splash:
            return await ctx.send(embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"{guild.name} has no splash"))
        await ctx.send(embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"[{guild.name}'s splash]({guild.splash})").set_image(url=guild.splash.url))

    
    @commands.hybrid_command(name='userinfo', description='shows info about a user', brief='user', usage='Send Messages', help="```Example: ;ui @jac#1337```", aliases=["ui", "whois"])
    async def userinfo(self, ctx, *, member: Union[discord.Member, discord.User] = None):
        async with ctx.typing():
            member = member or ctx.author
            fetched_user = ctx.guild.get_member(member.id)
            attempt = self.bot.get_user(member.id)
            if member in ctx.guild.members:
                device = []
                newmem = await self.bot.fetch_user(member.id)
                member = member or ctx.author
                discrims=['0001', '0002', '9999', '0666', '6666', '7777', '8888', '6900', '0069', '1337', '1000'] 
                badges = []
                headers = {"Authorization": f"Bearer {await get_spotify_token()}"}
                if fetched_user.discriminator in discrims:
                    if "<:BadgeNitro:925627225020194836> " not in badges and "<:BadgeNitro:925627225020194836> ":
                        badges.append('<:BadgeNitro:925627225020194836> ')
                if fetched_user == ctx.guild.owner:
                    badges.append('<:CrownGold:1003370254447157328>')
                if fetched_user.banner or fetched_user.premium_since and not '<a:0_boost15:921806976822956032>' in badges:
                    badges.append('<a:0_boost15:921806976822956032>')
                if fetched_user.id in devs and ctx.author.id in devs:
                    badges.append('<:VerifiedBotDev:921574550293073962> :money_mouth:')
                #if fetched_user.public_flags.verified_bot:
                    #badges.append('<:blurple_bot2:921812004715524157><:blurple_bot1:921812007798337546>')
                if fetched_user.is_on_mobile():
                    device.append("``📱 Mobile``")
                if fetched_user.web_status:
                    device.append("``🌐 Web``")
                if fetched_user.desktop_status:
                    device.append("``🖥️ Desktop``")
                desc = ""
                try:
                    spotify = discord.utils.find(lambda a: isinstance(a, discord.Spotify), fetched_user.activities)
                    name = spotify.title
                    song = spotify.artist
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://api.spotify.com/v1/search?query={spotify.title}&type=track&limit=1', headers=headers) as searchh:
                            search = await searchh.json()
                            if search["tracks"]["total"] > 0:
                                link = search["tracks"]["items"][0]["external_urls"]["spotify"]
                    desc += f'<a:spotify:921863335123750962> Listening to **[{name}]({link})** by **[{song}]({link})** on spotify..'
                except Exception as e:
                    print(e); pass

                try:
                    existing = await utils.index_user(self, bot=self.bot, author=fetched_user.id)
                    data=await utils.api_req(self, params=
                        {"user": f"{existing}", "method": "user.getrecenttracks", "limit": 1})
                    tracks = data["recenttracks"]["track"]
                    artist = tracks[0]["artist"]["#text"]
                    album = tracks[0]["album"]["#text"]
                    track = tracks[0]["name"]
                    image_url = tracks[0]["image"][-1]["#text"]
                    randomascii="—"
                    print(tracks[0])
                    nowplaying=tracks[0]["@attr"]
                    if nowplaying:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(f'https://api.spotify.com/v1/search?query={util.escape_md(track)}&type=track&limit=1', headers=headers) as searchh:
                                search = await searchh.json()
                                if search["tracks"]["total"] > 0:
                                    link = search["tracks"]["items"][0]["external_urls"]["spotify"]
                        desc += f"\n<:lastfm:939700245003128842> Listening to **[{util.escape_md(track)}]({link})** by **{util.escape_md(artist)}** on LastFM.."
                    else:
                        print('hi')
                except Exception as e:
                    print(e); pass

                embed = discord.Embed(title=f"{fetched_user} • {get_user_badges(user=member, fetched_user=fetched_user,bot=self.bot) or ''}{' '.join(badges)}", description=desc, color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), url='https://discord.gg/blame')
                if fetched_user.id in devs and not ctx.author.id == fetched_user.id:
                    embed.title = f'<:VerifiedBotDev:921574550293073962> {fetched_user} • **Blame Developer** <:VerifiedBotDev:921574550293073962>'
                    embed.set_image(url='https://c.tenor.com/_4YgA77ExHEAAAAd/rick-roll.gif')
                    return await ctx.send(embed=embed)
                embed.set_thumbnail(url=fetched_user.display_avatar.url)
                #view = discord.ui.View()
                #view.add
                #embed.add_field(name='__Badges:__', value=f"{get_user_badges(user=member, fetched_user=fetched_user,bot=self.bot)}{''.join(badges)}" or "No Badges", inline=False)
                embed.add_field(name=f"__Information__", value=f"**User:** ``{member}``\n**ID:** ``{member.id}``\n**Is bot:** ``{'False' if not member.bot else 'True'}``\n**Registered:** {discord.utils.format_dt(member.created_at, style='f')} **({discord.utils.format_dt(member.created_at, style='R')})**\n**Servers:** ``{len(member.mutual_guilds) if not member == ctx.me else len(self.bot.guilds)} shared``\n**Developer:** ``False``\n**Device:**" + ', '.join(device), inline=True)
                embed.add_field(name=f"__Guild Related__", value=f"**Joined:** {discord.utils.format_dt(member.joined_at, style='f')} **({discord.utils.format_dt(member.joined_at, style='R')})**\n**Join Position:** ``{sorted(ctx.guild.members, key=lambda m: m.joined_at or discord.utils.utcnow()).index(member) + 1}\{ctx.guild.member_count}``\n**Top role:** ``{member.top_role.name}``\n**Color:** ``{member.top_role.color}``\n**Status:** ``{member.status}``\n**Roles:** ``{len(member.roles)}``\n**Perms:** [``{member.top_role.permissions.value}``](https://discordapi.com/permissions.html)", inline=True)
                if newmem.banner:
                    link=newmem.banner.with_size(512)
                    embed.set_image(url=newmem.banner.url)

                                    
                perms = get_perms(member.guild_permissions)
                if perms:
                    embed.add_field(name=f"**__Permissions:__**",
                                    value=f"`{'` `'.join(perms)}`", inline=False)
                
                view = names(bot=self.bot, ctx=ctx, userr=member)
                return await ctx.send(embed=embed, view=view)
            if attempt:
                newmem = await self.bot.fetch_user(member.id)
                member = member or ctx.author
                discrims=['0001', '0002', '9999', '0666', '6666', '7777', '8888', '6900', '0069', '1337', '1000'] 
                badges = []
                headers = {"Authorization": f"Bearer {await get_spotify_token()}"}
                if attempt.discriminator in discrims:
                    if "<:BadgeNitro:925627225020194836> " not in badges and "<:BadgeNitro:925627225020194836> ":
                        badges.append('<:BadgeNitro:925627225020194836> ')
                if newmem.banner and not '<a:0_boost15:921806976822956032>' in badges:
                    badges.append('<a:0_boost15:921806976822956032>')
                if attempt.id in devs and ctx.author.id in devs:
                    badges.append('<:VerifiedBotDev:921574550293073962> :money_mouth:')
                desc = ""
                try:
                    spotify = discord.utils.find(lambda a: isinstance(a, discord.Spotify), attempt.activities)
                    name = spotify.title
                    song = spotify.artist
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://api.spotify.com/v1/search?query={spotify.title}&type=track&limit=1', headers=headers) as searchh:
                            search = await searchh.json()
                            if search["tracks"]["total"] > 0:
                                link = search["tracks"]["items"][0]["external_urls"]["spotify"]
                    desc += f'<a:spotify:921863335123750962> Listening to **[{name}]({link})** by **[{song}]({link})** on spotify..'
                except Exception as e:
                    print(e); pass

                try:
                    existing = await utils.index_user(self, bot=self.bot, author=attempt.id)
                    data=await utils.api_req(self, params=
                        {"user": f"{existing}", "method": "user.getrecenttracks", "limit": 1})
                    tracks = data["recenttracks"]["track"]
                    artist = tracks[0]["artist"]["#text"]
                    album = tracks[0]["album"]["#text"]
                    track = tracks[0]["name"]
                    image_url = tracks[0]["image"][-1]["#text"]
                    randomascii="—"
                    print(tracks[0])
                    nowplaying=tracks[0]["@attr"]
                    if nowplaying:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(f'https://api.spotify.com/v1/search?query={util.escape_md(track)}&type=track&limit=1', headers=headers) as searchh:
                                search = await searchh.json()
                                if search["tracks"]["total"] > 0:
                                    link = search["tracks"]["items"][0]["external_urls"]["spotify"]
                        desc += f"\n<:lastfm:939700245003128842> Listening to **[{util.escape_md(track)}]({link})** by **{util.escape_md(artist)}** on LastFM.."
                    else:
                        print('hi')
                except Exception as e:
                    print(e); pass

                embed = discord.Embed(title=f"{attempt} • {get_user_badges(user=attempt, fetched_user=attempt,bot=self.bot) or ''}{' '.join(badges)}", description=desc, color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), url='https://discord.gg/blame')
                if attempt.id in devs and not ctx.author.id == attempt.id:
                    embed.title = f'<:VerifiedBotDev:921574550293073962> {attempt} • **Blame Developer** <:VerifiedBotDev:921574550293073962>'
                    embed.set_image(url='https://c.tenor.com/_4YgA77ExHEAAAAd/rick-roll.gif')
                    return await ctx.send(embed=embed)
                embed.set_thumbnail(url=attempt.display_avatar.url)

                #embed.add_field(name='__Badges:__', value=f"{get_user_badges(user=member, fetched_user=fetched_user,bot=self.bot)}{''.join(badges)}" or "No Badges", inline=False)
                embed.add_field(name=f"__Information__", value=f"**User:** ``{member}``\n**ID:** ``{member.id}``\n**Is bot:** ``{'False' if not member.bot else 'True'}``\n**Registered:** {discord.utils.format_dt(member.created_at, style='f')} **({discord.utils.format_dt(member.created_at, style='R')})**\n**Servers:** ``{len(member.mutual_guilds)} shared``\n**Developer:** ``False``", inline=True)

                if newmem.banner:
                    link=newmem.banner.with_size(512)
                    embed.set_image(url=newmem.banner.url)
                                    

                view = names(bot=self.bot, ctx=ctx, userr=member)
                return await ctx.send(embed=embed, view=view)
            else:
                desc = ""
                fetched_user = member
                discrims=['0001', '0002', '9999', '0666', '6666', '7777', '8888', '6900', '0069', '1337', '1000'] 
                badges = []
                headers = {"Authorization": f"Bearer {await get_spotify_token()}"}
                if fetched_user.discriminator in discrims:
                    if "<:BadgeNitro:925627225020194836> " not in badges and "<:BadgeNitro:925627225020194836> " not in get_user_badges(user=member, fetched_user=fetched_user,bot=self.bot):
                        badges.append('<:BadgeNitro:925627225020194836> ')
                if fetched_user.avatar.is_animated() and not '<:BadgeNitro:925627225020194836> ' in badges and "<:BadgeNitro:925627225020194836> " not in get_user_badges(user=member, fetched_user=fetched_user,bot=self.bot):
                    badges.append('<:BadgeNitro:925627225020194836> ')
                if fetched_user.banner and not '<a:0_boost15:921806976822956032>' in badges:
                    badges.append('<a:0_boost15:921806976822956032>')
                if fetched_user.id in devs and ctx.author.id in devs:
                    badges.append('<:VerifiedBotDev:921574550293073962> :money_mouth:')


                embed = discord.Embed(title=f"{fetched_user} • {get_user_badges(user=member, fetched_user=fetched_user,bot=self.bot)}{' '.join(badges)}", description=desc, color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), url='https://discord.gg/blame')
                if fetched_user.id in devs and not ctx.author.id == fetched_user.id:
                    embed.title = f'<:VerifiedBotDev:921574550293073962> {fetched_user} • **Blame Developer** <:VerifiedBotDev:921574550293073962>'
                    embed.set_footer(text="STOP STALKING!")
                    embed.set_image(url='https://c.tenor.com/_4YgA77ExHEAAAAd/rick-roll.gif')
                    return await ctx.send(embed=embed)
                embed.set_thumbnail(url=fetched_user.display_avatar.url)
                #embed.add_field(name='__Badges:__', value=f"{get_user_badges(user=member, fetched_user=fetched_user,bot=self.bot)}{''.join(badges)}" or "No Badges", inline=False)
                embed.add_field(name=f"__Info__", value=f"**Username:** {member.name}", inline=True)
                embed.add_field(name=f"__Dates__",
                                value=
                                    f"\n**Registered:** {discord.utils.format_dt(member.created_at, style='f')} **({discord.utils.format_dt(member.created_at, style='R')})**", inline=False)
                                    
                embed.set_footer(text=f"ID: {member.id} • {len(fetched_user.mutual_guilds)} servers")
                await ctx.send(embed=embed)



    @commands.command()
    async def foo(self, ctx):
        return await ctx.reply("bar")
    
    @commands.command()
    async def bar(self, ctx):
        return await ctx.reply("foo")

    @commands.hybrid_command()
    async def invites(self, ctx, member: discord.Member=None):
        if member == None:
            member = ctx.author
            totalInvites = 0
            for i in await ctx.guild.invites():
                if i.inviter == ctx.author:
                    totalInvites += i.uses
            em = discord.Embed(description=f"<:FFinfo:926308238322987058> You have **{totalInvites}** invite(s)", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
            await ctx.send(embed=em)
        else:
            totalInvites = 0
            for i in await ctx.guild.invites():
                if i.inviter == member:
                    totalInvites += i.uses
            bluecheck = self.bot.get_emoji(807804663297736754)
            em = discord.Embed(description=f"<:FFinfo:926308238322987058> <@{member.id}> has {totalInvites} invite(s)", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
            await ctx.send(embed=em)


    @commands.hybrid_command(name='botinfo', aliases=['about', 'info', 'botstats'],description='show info about the bot', usage='Send Messages')
    async def botinfo(self, ctx):
        async with ctx.typing():
            bc = sum(chain([len(_.members) for _ in self.bot.guilds]))
            stats=await self.bot.db.command('dbStats')
            find = await self.db.find_one({"start": "June 8th, 2022"})
            count = find['count']
            rows=stats['dataSize']
            tables=stats['storageSize']
            bc =sum(self.bot.get_all_members())
            process_uptime=time.time() - self.bot.start_time
            system_uptime=time.time() - psutil.boot_time()
            system_uptime=util.stringfromtime(system_uptime, 2)
            data = await util.get_commits("inadvertently", "blamev2")
            last_update = data[0]["commit"]["author"].get("date")
            uptime=util.stringfromtime(process_uptime, 2)
            embed = discord.Embed(title=f"<:FFinfo:926308238322987058> blame",url="https://blame.gg", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"**Developers** <@!236522835089031170>, <@!714703136270581841>, <@!386192601268748289>\n**Redefining versatility since:** {discord.utils.format_dt(self.bot.user.created_at, style='R')}")
            #\nRegistered: **{int(av):,}**
            try:
                embed.add_field(name="__Statistics:__", value=f"Users: **{bc:,}**\nGuilds: **{len(self.bot.guilds):,}**")
                embed.add_field(name="__Usage:__", value=f"Commands: **{sum(chain(1 for i in self.bot.walk_commands()))}**\nRan: **{count:,}**")
                embed.add_field(name='Uptime', value=f"Bot: **{uptime}**\nSystem: **{system_uptime}**", inline=True)
                #embed.add_field(name="__Data:__", value=f"``[{tables:,}](https://discord.gg/blame)`` tables\n``[{rows:,}](https://discord.gg/blame)`` rows\n``[1ms](https://docs.blame.gg)`` db latency")
                embed.set_footer(text=f"Latest update: {arrow.get(last_update).humanize()} | The Blame Team").set_thumbnail(url=self.bot.user.avatar.url)
                embed.set_thumbnail(url=self.bot.user.avatar.url)

                embed.add_field(
                    name="Data",
                    value=f"```rb\nlines: {await count_lines('./', '.py'):,} | Tables: {tables:,}"
                    f"\nfunctions: {await count_others('./', '.py', 'def '):,} | Rows: {rows:,}"
                    f"\nclasses: {await count_others('./', '.py', 'class '):,} | Latency: 1ms\n```",
                )
            except (FileNotFoundError, UnicodeDecodeError):
                pass
            await ctx.send(embed=embed)


    @commands.hybrid_command(aliases=['inv'])
    async def invite(self, ctx):
        if not ctx.guild.id == 818179462918176769:
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/Xa2ZJr4atx"))
            embed = discord.Embed(description="To invite **blame** you **must be **joined** in the [support server](https://discord.gg/Xa2ZJr4atx)** and **retry this command**", color=0x2F3136)
            await ctx.reply(f"""{ctx.author.mention}  ||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​|||||||||||| https://discord.gg/Xa2ZJr4atx""", embed=embed, view=view)
        else:
            embed = discord.Embed()
            embed = discord.Embed(description="**Invites**\n[Our support server](https://discord.gg/EGj2GzpU9s) \n[Invite blame](https://discord.com/api/oauth2/authorize?client_id=776128410547126322&permissions=8&scope=bot)\n\nRaw invite link: https://discord.com/api/oauth2/authorize?client_id=776128410547126322&permissions=8&scope=bot", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), timestamp=ctx.message.created_at)
            embed.set_footer(text="Thanks for using blame 👍", icon_url=ctx.guild.icon.url)
            view = test()
            await ctx.send(embed=embed, view=view)

    @commands.command(aliases=['raw', 'rawinvite'])
    async def link(self, ctx):
        return await ctx.reply('https://discord.com/api/oauth2/authorize?client_id=776128410547126322&permissions=8&scope=bot')

    @commands.command()
    async def support(self, ctx):
        return await ctx.reply('https://discord.gg/Xa2ZJr4atx')

    async def linecount(self):
        total = 0
        file_amount = 0
        for path, _, files in os.walk("."):
            for name in files:
                file_dir = str(pathlib.PurePath(path, name))
                if not name.endswith(".py"):
                    continue
                file_amount += 1
                with open(file_dir, "r", encoding="utf-8") as file:
                    for line in file:
                        if not line.strip().startswith("#") or not line.strip():
                            total += 1
                return f"{total}-{file_amount}"


    @commands.command(name='color', description="show a hex code's info", help="```Example: ;color #303135```", brief="hex/color/image/member")
    async def color(self, ctx, *sources):
        if not sources:
            return await util.send_command_help(ctx)

        colors = []
        i = 0
        while i < len(sources):
            source = sources[i]
            i += 1
            if source.lower() == "random":
                try:
                    amount = int(sources[i])
                    i += 1
                except (IndexError, ValueError):
                    amount = 1

                for _ in range(min(amount, 50)):
                    colors.append("{:06x}".format(random.randint(0, 0xFFFFFF)))
                continue

            role_or_user = await util.get_member(ctx, source) or await util.get_role(ctx, source)
            if role_or_user is not None:
                colors.append(str(role_or_user.color).strip("#"))
                continue

            if source.startswith("http") or source.startswith("https"):
                url_color = await util.color_from_image_url(source)
                if url_color is not None:
                    colors.append(url_color)
                    continue

            color = await util.get_color(ctx, "#" + source.strip("#"))
            if color is not None:
                colors.append(str(color))
                continue

            await ctx.send(f"Error parsing `{source}`")

        if not colors:
            return await ctx.send("No valid colors to show")

        content = discord.Embed(colour=await util.get_color(ctx, "#" + colors[0].strip("#")))

        if len(colors) > 50:
            await ctx.send("Maximum amount of colors is 50, ignoring rest...")
            colors = colors[:50]

        colors = [x.strip("#") for x in colors]
        url = "https://api.color.pizza/v1/" + ",".join(colors)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                colordata = (await response.json()).get("colors")

        if len(colors) == 1:
            discord_color = await util.get_color(ctx, "#" + colors[0].strip("#"))
            hexvalue = colordata[0]["requestedHex"]
            rgbvalue = discord_color.to_rgb()
            name = colordata[0]["name"]
            luminance = colordata[0]["luminance"]
            image_url = f"http://www.colourlovers.com/img/{colors[0]}/200/200/color.png"
            content.title = name
            content.description = (
                f"**HEX:** `{hexvalue}`\n"
                f"**RGB:** {rgbvalue}\n"
                f"**Luminance:** {luminance:.4f}"
            )
            content.set_image(url=image_url)
            return await ctx.send(embed=content)
        else:
            content.description = ""
            palette = ""
            for i, color in enumerate(colors):
                hexvalue = colordata[i]["requestedHex"]
                name = colordata[i]["name"]
                content.description += f"`{hexvalue}` **| {name}**\n"
                palette += color.strip("#") + "/"

            image_url = f"https://www.colourlovers.com/paletteImg/{palette}palette.png"

            content.set_image(url=image_url)
            return await ctx.send(embed=content)

    @commands.command(aliases=["ud"], description="Search for a definition from urban dictionary", help="```Example: ;urban leet```",brief='word')
    async def urban(self, ctx, *, word):
        url = "https://api.urbandictionary.com/v0/define"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"term": word}) as response:
                data = await response.json()
        pages = []
        if data["list"]:
            for entry in data["list"]:
                definition = entry["definition"].replace("]", "**").replace("[", "**")
                example = entry["example"].replace("]", "**").replace("[", "**")
                timestamp = entry["written_on"]
                content = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                content.description = f"{definition}"
                if not example == "":
                    content.add_field(name="Example", value=example)
                content.set_footer(text=f"by {entry['author']} • "f"{entry.get('thumbs_up')} 👍 {entry.get('thumbs_down')} 👎")
                content.timestamp = arrow.get(timestamp).datetime
                content.set_author(name=entry["word"],icon_url="https://i.imgur.com/yMwpnBe.png",url=entry.get("permalink"),)
                pages.append(content)
            await util.page_switcher(ctx, pages)
        else:
            await ctx.send(f"No definitions found for `{word}`")

    @commands.hybrid_command(
        aliases = ['sp', 'spot'],
        usage = 'send_messages',
        description = 'View yours, another members, or search for a specific spotify track',
        brief = 'member[Optional], track[Optional]',
        help = "```Syntax: spotify [track] or [member]\nExample: spotify @jacob```"
    )
    async def spotify(self, ctx, *, query=None):
        member = ctx.author
        headers = {"Authorization": f"Bearer {await get_spotify_token()}"}
        if query == None:
            try:
                spotify = discord.utils.find(lambda a: isinstance(a, discord.Spotify), member.activities)
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'https://api.spotify.com/v1/search?query={spotify.title}&type=track&limit=1', headers=headers) as searchh:
                        search = await searchh.json()
                        name = None
                        artist = None
                        link = None

                        if search["tracks"]["total"] > 0:
                            link = search["tracks"]["items"][0]["external_urls"]["spotify"]
                            name = search["tracks"]["items"][0]["name"]
                            artists = []
                            for artist in search["tracks"]["items"][0]["artists"]:
                                artists.append(artist["name"])
                            await ctx.send(f"{link}")
                        else:
                            await ctx.send(f"{link}") 
            except:
                pass; return await ctx.send("You're not listening to anything. Try searching for a song instead")
        else:    
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.spotify.com/v1/search?query={query}&type=track&limit=1', headers=headers) as searchh:
                    search = await searchh.json()
                    name = None
                    artist = None
                    link = None

                    if search["tracks"]["total"] > 0:
                        link = search["tracks"]["items"][0]["external_urls"]["spotify"]
                        name = search["tracks"]["items"][0]["name"]
                        artists = []
                        for artist in search["tracks"]["items"][0]["artists"]:
                            artists.append(artist["name"])
                        await ctx.send(f"{link}")
                    else:
                        await ctx.send(f"{link}")

    @commands.hybrid_command(name="charinfo", description="Get info on a character")
    async def charinfo(self, ctx, *, text):
        if len(text) > 20:
            return await ctx.send("Your text must be shorter than 20 characters.")

        info = []
        for character in text:
            digit = f"{ord(character):x}"
            name = unicodedata.name(character, "Name not found")
            info.append(f"**{name}** - {character} (`\\U{digit:>08}`)  <http://www.fileformat.info/info/unicode/char/{digit}>")
        embed = discord.Embed(description=f":information_source: {ctx.author.mention}: " + "".join(info), color=0x3b88c3)
        await ctx.send(embed=embed)

    @commands.command(help="Generate an image of you tweeting something")
    async def tweet(self, ctx, *, text: str):
        member = ctx.author
        if len(text) >= 1000:
            return await ctx.send('too long')

        avatar = member.display_avatar.url
        embed = discord.Embed()
        embed.set_image(
            url=f"https://some-random-api.ml/canvas/tweet?comment={text}&avatar={avatar}&username={member.name}&displayname={member.display_name}"
        )
        await ctx.send(embed=embed)

    @commands.command(help="Find the lyrics of the song specified")
    async def lyrics(self, ctx, song:str):
        async with ctx.typing():
            msg = await ctx.send(embed=discord.Embed(description=":mag_right: **Searching..**", color=discord.Color.blurple()))
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'https://some-random-api.ml/lyrics?title={song}') as r:
                        j = await r.json()
            except: pass; return await ctx.send("Failed, please report this in the support server")
            entries=[
                j["lyrics"][i : i + 140] for i in range(0, len(j["lyrics"]), 140)
            ]
            embedss= []
            for i in entries:
                embed = discord.Embed(timestamp=ctx.message.created_at, color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                embed.set_author(name=f"Song: {j['title']}", icon_url=j["thumbnail"]["genius"])
                embed.set_thumbnail(url=j["thumbnail"]["genius"])
                embed.description = i
                embedss.append(embed)
                embed.set_footer(text=f"Pages: {len(embedss)}/{len(entries)}")
            await msg.delete()
            paginator = pg.Paginator(self.bot, embedss, ctx, invoker=ctx.author.id)
            if len(embedss) > 1:
                paginator.add_button('prev', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.blurple)
                paginator.add_button('next', emoji='<:right:934237462660788304>', style=discord.ButtonStyle.blurple)
            return await paginator.start()
            # 
            # await util.send_as_pages(ctx, embed, rows)

    @commands.command(
        aliases = ['badgecount', 'badge'],
        usage = 'Send messages',
        description = "View badge statistics within your server",
        brief = 'None',
        help = "```Example: badges```"
    )
    async def badges(self, ctx):
        first = discord.Embed(title=f"<a:loading:921613350310383666> Analyzing {len(ctx.guild.members)}...", color=discord.Color.blurple())
        firstsend = await ctx.send(embed=first)
        await asyncio.sleep(0.8)
        second = discord.Embed(title=f"{ctx.guild.name} Badge Statistics", description=f"<:staff:921574394084618330> Discord Staff: **{len([m for m in ctx.guild.members if m.public_flags.staff])}**\n<:BadgeBugHunter:925625840488816700> Bug Hunter: **{len([m for m in ctx.guild.members if m.public_flags.bug_hunter])}**\n<:BadgeBugHunterLvl2:925644695479144478> Bug Hunter Level 2: **{len([m for m in ctx.guild.members if m.public_flags.bug_hunter_level_2])}**\n<:Moderator:985597978574200832> Discord Certified Moderator: **{len([m for m in ctx.guild.members if m.public_flags.discord_certified_moderator])}**\n<:badge_earlysupporter:921544103039230032> Early Supporter: **{len([m for m in ctx.guild.members if m.public_flags.early_supporter])}**\n<:VerifiedBotDev:921574550293073962> Early Verified Bot Developer: **{len([m for m in ctx.guild.members if m.public_flags.early_verified_bot_developer])}**\n<:CB_hypesquad:921544078468984843> Hypesquad: **{len([m for m in ctx.guild.members if m.public_flags.hypesquad])}**\n<:badge_balance:921544098773614612> Hypesquad Balance: **{len([m for m in ctx.guild.members if m.public_flags.hypesquad_balance])}**\n<:badge_bravery:921544099981570091> Hypesquad Bravery: **{len([m for m in ctx.guild.members if m.public_flags.hypesquad_bravery])}**\n<:badge_brilliance:921544101726392320> Hypequad Brilliance: **{len([m for m in ctx.guild.members if m.public_flags.hypesquad_brilliance])}**\n<:BadgePartner:925624836993204235> Discord Partner: **{len([m for m in ctx.guild.members if m.public_flags.partner])}**\n<:blurple_bot2:921812004715524157><:blurple_bot1:921812007798337546> Verified Bots: **{len([m for m in ctx.guild.members if m.public_flags.verified_bot])}**\n<:bot:921595812956479499> Bots: **{len([m for m in ctx.guild.members if m.bot and not m.public_flags.verified_bot])}**\n<a:0_boost1:921806963359252480> Boosters: **{len(ctx.guild.premium_subscribers)}**", color=discord.Color.blurple())
        second.set_footer(text=f"Total: {len(ctx.guild.members)}")
    
        await firstsend.edit(embed=second)

    @commands.command(
        aliases=['channel', 'cinfo', 'ci'],
        usage = "View channel",
        description = "View certain channel information on the given channel",
        brief = "channel",
        help = "```Syntax: channelinfo [channel]\nExample: channelinfo #general```"
        )
    async def channelinfo(self, ctx, *, channel: int = None):
        if not channel:
            channel = ctx.message.channel
        else:
            channel = self.bot.get_channel(channel)
        data = discord.Embed()
        data.set_thumbnail(url=f"{ctx.guild.icon.url}")
        data.set_author(name=f"{ctx.guild.name}", icon_url=ctx.guild.icon.url)
        if hasattr(channel, 'mention'):
            data.description = "**Channel:** " + channel.mention
        if hasattr(channel, 'changed_roles'):
            if len(channel.changed_roles) > 0:
                data.color = discord.Colour.blurple()
        if isinstance(channel, discord.TextChannel): 
            _type = "Text"
        elif isinstance(channel, discord.VoiceChannel): 
            _type = "Voice"
        else: 
            _type = "Unknown"
        data.add_field(name="Type", value=_type)
        data.add_field(name="ID", value=channel.id, inline=False)
        if hasattr(channel, 'position'):
            data.add_field(name="Position", value=channel.position)
        if isinstance(channel, discord.VoiceChannel):
            if channel.user_limit != 0:
                data.add_field(name="User Number", value="{}/{}".format(len(channel.voice_members), channel.user_limit))
            else:
                data.add_field(name="User Number", value="{}".format(len(channel.voice_members)))
            userlist = [r.display_name for r in channel.members]
            if not userlist:
                userlist = "None"
            else:
                userlist = "\n".join(userlist)
            data.add_field(name="Users", value=userlist)
            data.add_field(name="Bitrate", value=channel.bitrate)
        elif isinstance(channel, discord.TextChannel):
            try:
                pins = await channel.pins()
                data.add_field(name="Pins", value=len(pins), inline=True)
            except discord.Forbidden:
                pass
            data.add_field(name="Members", value="%s"%len(channel.members))
            if channel.topic:
                data.add_field(name="Topic", value=channel.topic, inline=False)
            hidden = []
            allowed = []
            for role in channel.changed_roles:
                if role.permissions.read_messages is True:
                    if role.name != "@everyone":
                        allowed.append(role.mention)
                elif role.permissions.read_messages is False:
                    if role.name != "@everyone":
                        hidden.append(role.mention)
            if len(allowed) > 0: 
                data.add_field(name='Allowed Roles ({})'.format(len(allowed)), value=', '.join(allowed), inline=False)
            if len(hidden) > 0:
                data.add_field(name='Restricted Roles ({})'.format(len(hidden)), value=', '.join(hidden), inline=False)
        if channel.created_at:
            data.set_footer(text=("Created on {} ({} days ago)".format(channel.created_at.strftime("%d %b %Y %H:%M"), (ctx.message.created_at - channel.created_at).days)))
        await ctx.send(embed=data)

    @commands.command()
    async def change_av(self, ctx, url: str = None):
        """ Change avatar_ """
        if ctx.author.id in devs:
            if url is None and len(ctx.message.attachments) == 1:
                url = ctx.message.attachments[0].url
            else:
                url = url.strip("<>") if url else None

            try:
                bio = await http.get(url, res_method="read")
                await ctx.send(f"sucess")
                return await self.bot.user.edit(avatar=bio)
            except aiohttp.InvalidURL:
                await ctx.send("The URL is invalid...")
            except discord.HTTPException as err:
                await ctx.send(err)
            except TypeError:
                await ctx.send("You need to either provide an image URL or upload one with the command")
            except:
                await ctx.send("This URL does not contain a useable image")
        else:
            return
    
    @commands.command(aliases = ['ii'])
    async def inviteinfo(self, ctx, inv):
        if inv.startswith('https'):
            zzz = inv.rsplit('/')
            inv = zzz[3]
            print(inv)
        if inv.startswith('discord.gg'):
            zzz = inv.rsplit('/')
            inv = zzz[1]
            print(inv)
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://discord.com/api/v9/invites/{inv}") as b:
                a = await b.json()
                if 'inviter' in a:
                    data = a['guild']
                    data2 = a['inviter']
                    name = data['name']
                    id = data['id']
                    description = data['description']
                    if description == None:
                        description = 'No description'
                    icon = data['icon']
                    boosts = data['premium_subscription_count']
                    invi= data2['username']
                    ter= data2['discriminator']
                    inviter = f"{invi}#{ter}"
                    emoji =''
                    level =''
                    if int(boosts) < 3:
                        emoji += '<:boosterbadge:921561063340785696>'
                        level += '1'
                    if int(boosts) < 8:
                        emoji += '<:TNT_9booster:1022274008990879835>'
                        level += '2'
                    if int(boosts) < 15:
                        emoji += '<:ServerBoostTier3:1022273962006282282>'
                        level += '3'
                    else:
                        emoji += '<:ServerBoostTier3:1022273962006282282>'
                        level += '3'
                    features = data['features']
                    desc = ""
                    for i in features:
                        desc += f"{i}, "
                    print(emoji)
                    embed= discord.Embed(title = f'Invite Info for /{inv}', url=f"https://discord.gg/{inv}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"<:FFinfo:926308238322987058> **{description}**")
                    embed.set_author(name=f"{name} ({id})", url=f"https://discord.gg/{inv}", icon_url=f"https://cdn.discordapp.com/icons/{id}/{icon}")
                    embed.set_thumbnail(url=f"https://cdn.discordapp.com/icons/{id}/{icon}")
                    embed.add_field(name="Invite:", value=f"**[/{inv}](https://discord.gg/{inv})**")
                    embed.add_field(name="Server:", value=f"{name}")
                    embed.add_field(name="Boosts:", value=f"{emoji} Level: **{level}/{boosts} boosts**")
                    embed.add_field(name='Features:', value=f'```{desc}```', inline=False)
                    embed.set_footer(text=f"Invite created by {inviter}", icon_url=ctx.author.display_avatar.url)
                    await ctx.send(embed=embed)
                if 'message' in a:
                    return await util.send_error(ctx, 'Unknown Invite')
                else:
                    data = a['guild']
                    name = data['name']
                    id = data['id']
                    description = data['description']
                    if description == None:
                        description = 'No description'
                    icon = data['icon']
                    boosts = data['premium_subscription_count']
                    emoji =''
                    level =''
                    if int(boosts) < 3:
                        emoji += '<:boosterbadge:921561063340785696>'
                        level += '1'
                    if int(boosts) < 8:
                        emoji += '<:TNT_9booster:1022274008990879835>'
                        level += '2'
                    if int(boosts) < 15:
                        emoji += '<:ServerBoostTier3:1022273962006282282>'
                        level += '3'
                    else:
                        emoji += '<:ServerBoostTier3:1022273962006282282>'
                        level += '3'
                    features = data['features']
                    desc = ""
                    for i in features:
                        desc += f"{i}, "
                    print(emoji)
                    embed= discord.Embed(title = f'Invite Info for /{inv}', url=f"https://discord.gg/{inv}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"<:FFinfo:926308238322987058> **{description}**")
                    embed.set_author(name=f"{name} ({id})", url=f"https://discord.gg/{inv}", icon_url=f"https://cdn.discordapp.com/icons/{id}/{icon}")
                    embed.set_thumbnail(url=f"https://cdn.discordapp.com/icons/{id}/{icon}")
                    embed.add_field(name="Invite:", value=f"**[/{inv}](https://discord.gg/{inv})**")
                    embed.add_field(name="Server:", value=f"{name}")
                    embed.add_field(name="Boosts:", value=f"{emoji} Level: **{level}/{boosts} boosts**")
                    embed.add_field(name='Features:', value=f'```{desc}```')
                    embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.display_avatar.url)
                    await ctx.send(embed=embed)



    @commands.command(aliases=["snapcode", 'snap'])
    async def snapchat(self, ctx, *, username):
        try:
            async with ctx.typing():
                    url = f"https://app.snapchat.com/web/deeplink/snapcode?username={username}&type=SVG"
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as s:
                            page = await s.text()
                            soup = BeautifulSoup(page, features="xml")
                            zz = f"{soup}"
                            dict_resp = xmltodict.parse(zz)
                            z=dict_resp['svg']["image"]['@xlink:href']
                            new = z.replace('data:image/png;base64,', '')
                            image = Image.open(BytesIO(base64.b64decode(str(new))))
                            image.save('blame_snapchat.png', 'PNG')
                    async def binary():
                        with open('blame_snapchat.png', "rb") as fh:
                            return BytesIO(fh.read())  
                    await ctx.reply(f"<a:snapchat:921863351070494760> **{username}'s** snapcode", file=discord.File(fp=await binary(), filename='blame_snapchat.png'))
        except Exception as e:
            print(e)
            pass
            return await ctx.send("Couldn't scrape that snapchat")            
        await asyncio.sleep(2)
        os.remove('blame_snapchat.png')


    @commands.command(
        aliases = ['ann', 'ance'],
        usage = "Mention everyone, Manage messages",
        description = "Send an announcement through the bot to a specific channel",
        brief = "Channel, Message",
        help = f"```Syntax: announce [channel] [message]\nExample: announce 851633587915587615 use blame bot!..``` "
    )
    @commands.has_permissions(mention_everyone=True, manage_messages=True)
    async def announce(self, ctx, channel: discord.TextChannel=None, *, message=None):
        if channel==None:
            return await ctx.send(f"Please try ``help announce`` for correct format.")
        if message==None:
            return await ctx.send(f"Please try ``help announce`` for correct format.")
        if len(message) > 2000:
            return await ctx.send("Message cannot be greater than 2000 characters")
        else:
            await channel.send(message)
            return await ctx.message.add_reaction("✅")

    @commands.command()
    async def privacy(self, ctx):
        await ctx.reply("""**Privacy Policy** *as of 09/05/2022*

> **What do we store and why?**
Blames storage depends on various factors. **Ex:** If you use the antinuke and are ``whitelisted``, your ID is now stored until you're ``unwhitelisted``. Certain things like, ``antiraid ignore`` also **temporarily** stores the user's ID until x time. The most commonly stored data would probably have to be server id's as they allow you to ``enable`` & ``disable`` certain modules per guild.

**Commonly asked questions revolving privacy:**

> **Is my data being used?**
In the literal sense, yes, your data is being used **to function** certain modules that you **agreed** to. In further depth, the only **data** we have and use from you is your **ID**. We use your ID to validate certain checks within modules and commands that then allow you to use them. Your **data** is never used for/with malicious intent.

> **Can anyone see my data?**
No, you data remains within our database systems **away** from user interaction/exposure.

> **Can I opt-out of my data being collected?**
Yes, you can **most definitely opt-out.** We actually give you the option to do so upon your **first command** being ran.  **Notice:** If you decide to opt-out, you **will not** be able to use blame as we rather save the resources.

> **How do I opt-in?**
Accidently opt-out? Join the **support server** and ping any of the staff team""")

    @commands.command(aliases = ['solved', 'close'])
    @commands.has_permissions(manage_messages=True)
    async def closed(self, ctx):
        if ctx.guild.id == 818179462918176769:
            await ctx.send(f"<:check:1027703035054526475> **Solved!** This post will be **closing in 5 minutes** - {ctx.author.mention}")
            await ctx.channel.edit(name="SOLVED")
            await asyncio.sleep(300)
            await ctx.channel.edit(locked=True, archived=True)
        else:
            return

    @commands.hybrid_command()
    async def ping(self, ctx):
        msg = await ctx.send("**pinging**")
        await msg.edit(content=f"**ping:** ``{round (self.bot.latency * 1000)}ms``")

    @commands.command()
    async def pinger(self, ctx):
        pings = []
        embed2 = discord.Embed(description="**Pinging**", color=discord.Color.blurple())
        start = time.perf_counter()
        msg = await ctx.send(embed=embed2)
        end = time.perf_counter()
        raa = (end - start) * 1000
        ra = round(self.bot.latency * 1000)
        pings.append(ra)
        await asyncio.sleep(0.2)
        ping1 = discord.Embed(description=f"Reading 1: **{ra}ms**", colour = discord.Color.blurple())
        start1 = time.perf_counter()
        await msg.edit(embed=ping1)
        end1 = time.perf_counter()
        ra11 = (end1 - start1) * 1000
        ra1 = round(self.bot.latency * 1000)
        pings.append(ra1)
        await asyncio.sleep(0.2)
        ping2 = discord.Embed(description=f"Reading 1: **{ra}ms**\nReading 2: **{ra1}ms**", colour = discord.Color.blurple())
        start2 = time.perf_counter()
        await msg.edit(embed=ping2)
        end2 = time.perf_counter()
        ra22 = (end2 - start2) * 1000
        ra2 = round(self.bot.latency * 1000)
        pings.append(ra2)
        await asyncio.sleep(0.2)
        ping3 = discord.Embed(description=f"Reading 1: **{ra}ms**\nReading 2: **{ra1}ms**\nReading 3: **{ra2}ms**", colour = discord.Color.blurple())
        start3 = time.perf_counter()
        await msg.edit(embed=ping3)
        end3 = time.perf_counter()
        ra222 = (end3 - start3) * 1000
        ra3 = round(self.bot.latency * 1000)
        pings.append(ra3)
        ping4 =discord.Embed(description=f"Reading 1: **{ra}ms**\nReading 2: **{ra1}ms**\nReading 3: **{ra2}ms**\nReading 4: **{ra3}ms**", colour = discord.Color.blurple())
        await msg.edit(embed=ping4)
        await asyncio.sleep(0.2)
        avg1 = sum(pings)/len(pings)
        avg = round(avg1, 2)
        final = discord.Embed(description=f"Reading 1: **{ra}ms**\nReading 2: **{ra1}ms**\nReading 3: **{ra2}ms**\nReading 4: **{ra3}ms**\n\n<a:connection:921613239471706142> **{avg}ms**", colour = discord.Color.blurple())
        await msg.edit(embed=final)

    @commands.command(
        aliases = ['fban', 'yeet', 'bann'],
        usage = 'Send messages',
        description = "Fake ban a member from the server",
        brief = "member, reason",
        help = '```Syntax: fban [member] [reason]\nExample: fban @jacob sus concerning jokes```'
    )
    async def fakeban(self, ctx, member: discord.Member=None, *, reason=None):
        if member == None:
            return await ctx.send("Provide a user to fban")
        if reason == None:
            return await ctx.send(f"**{member}** has been banned from {ctx.guild.name} ** -- unable to send dm**")
        else:
            await ctx.send(f"**{member}** has been banned from {ctx.guild.name} - **{reason}**")


    @commands.command(
        aliases = ['bannerset', 'changebanner', 'newbanner', 'setserverbanner'],
        usage = 'Manage guild',
        description = "Change the servers banner to the given one",
        brief = 'image_url, image',
        help = "```Syntax: setbanner [image_url]\nExample: setbanner https://blame.gg/avatars/blameicon.png?size=960```"
    )
    @commands.has_permissions(manage_guild=True)
    async def setbanner(self, ctx, image_url=None):
        vaild_urls = ['https', 'http']
        attachments = ctx.message.attachments
        #if image_url == None:
            #return await ctx.send("Please provide an image or image_url")
        if str(image_url).lower().startswith(tuple(vaild_urls)):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as r:
                        read = await r.read()
                await ctx.guild.edit(banner=read, reason=f"Requested by {ctx.author}")
                return await ctx.send("success")
            except Exception as e:
                return await ctx.send("Improper url")
        if attachments:
            async with aiohttp.ClientSession() as session:
                async with session.get(attachments[0].url) as r:
                    scan = await r.read()
            await ctx.guild.edit(banner=scan, reason=f"Requested by {ctx.author}")
            return await ctx.send("success")
        else:
            return await ctx.send("Please provide a supported image or image_url")

    @commands.command(
        aliases = ['setguildicon', 'setserverpfp', 'setservericon'],
        usage = "Manage guild",
        description = "Change the servers icon to the given one",
        brief = 'image_url, image',
        help = f"```Syntax: seticon [image_url]\nExample: seticon https://blame.gg/avatars/blameicon.png?size=1024```"
    )
    @commands.has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def seticon(self, ctx, image_url=None):
        vaild_urls = ['https', 'http']
        attachments = ctx.message.attachments
        #if image_url == None:
            #return await ctx.send("Please provide an image or image_url")
        if str(image_url).lower().startswith(tuple(vaild_urls)):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as r:
                        read = await r.read()
                await ctx.guild.edit(icon=read, reason=f"Requested by {ctx.author}")
                return await ctx.send("success")
            except Exception as e:
                return await ctx.send("Improper url")
        if attachments:
            async with aiohttp.ClientSession() as session:
                async with session.get(attachments[0].url) as r:
                    scan = await r.read()
            await ctx.guild.edit(icon=scan, reason=f"Requested by {ctx.author}")
            return await ctx.send("success")
        else:
            return await ctx.send("Please provide a supported image or image_url")

    @commands.command(
        usage = "Manage guild",
        description = "Change the servers splash to the given one",
        brief = 'image_url, image',
        help = f"```Syntax: setsplash [image_url]\nExample: setsplash https://blame.gg/avatars/blameicon.png?size=1024```"
    )
    @commands.has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def setsplash(self, ctx, image_url=None):
        vaild_urls = ['https', 'http']
        attachments = ctx.message.attachments
        #if image_url == None:
            #return await ctx.send("Please provide an image or image_url")
        if str(image_url).lower().startswith(tuple(vaild_urls)):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as r:
                        read = await r.read()
                await ctx.guild.edit(splash=read, reason=f"Requested by {ctx.author}")
                return await ctx.send("success")
            except Exception as e:
                return await ctx.send("Improper url")
        if attachments:
            async with aiohttp.ClientSession() as session:
                async with session.get(attachments[0].url) as r:
                    scan = await r.read()
            await ctx.guild.edit(splash=scan, reason=f"Requested by {ctx.author}")
            return await ctx.send("success")
        else:
            return await ctx.send("Please provide a supported image or image_url")

    @commands.command(
        usage = "Send Messages",
        description = "View yours or another member's status",
        brief = 'member',
        help = "```Syntax: status [member]\nExample: status @jacob```"
    )
    async def status(self, ctx, member: discord.Member=None):
        if member == None:
            member = ctx.author
        for s in member.activities:
            if isinstance(s, discord.CustomActivity):
                return await ctx.send(f"{member.name} status is **{s}** ")
            else:
                return await ctx.send(f"{member.name} has no custom status")
    
    @commands.command(
        usage = "send_messages",
        description = "Convert text to speech",
        brief = 'text',
        help = "```Syntax: tts [text]\nExample: tts sup jacob"
    )
    async def tts(self, ctx, *, text):
        mp3_fp = io.BytesIO()
        tts = gTTS(str(text), lang='en')
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return await ctx.send(file=discord.File(mp3_fp, "blame_TTS.mp3")) 

    @commands.command(aliases = ['source'])
    async def src(self, ctx):
        return await ctx.send("My source code can be found here: https://github.com/inadvertently/Blame")

async def setup(client): 
    await client.add_cog(miscc(client))
