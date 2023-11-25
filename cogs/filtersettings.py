import discord, motor.motor_asyncio, Core.utils as utils, re
from discord.ext import commands, tasks
from Core.utils import get_theme
import button_paginator as pg

def strip_codeblock(content):
    if content.startswith('```') and content.endswith('```'):
        return content.strip('```')
    return content.strip('` \n')

class Flags(commands.FlagConverter, prefix='--', delimiter=' ', case_insensitive=True):
    @classmethod
    async def convert(cls, ctx, argument: str):
        argument = strip_codeblock(argument).replace(' —', ' --')
        return await super().convert(ctx, argument)
    do: str 
    limit: int


class serversettings(commands.Cog):
    def __init__(self, client):
        self.bot = client  
        self.image = self.bot.db['imagefilter']
        self.imagelock = self.bot.db['imagelock']
        self.invites = self.bot.db['invites']
        self.links = self.bot.db['links']
        self.db = self.bot.db["settings welcome"]
        self.sticky = self.bot.db['sticky']
        self.bans = self.bot.db['bans']
        self.urgecolor = 0xF3DD6C
        self.errorcol = 0xA90F25 # error color
        self.success = discord.Colour.blurple() #theme
        self.checkmoji = "<:blurple_check:921544108252741723>" # success emoji
        self.xmoji = "<:yy_yno:921559254677200957>" # unsuccessful emoji
        self.urgentmoji = "<:n_:921559211366838282>" # exclamation emoji
        self.invitescache = {}
        self.linkscache = {}
        self.imagecache = {}
        self.imagelockcache = {}
        self.stickycache = {}
        self.cache = {}
        self.joins = {}
        self.cacheInvites.start()
        self.cacheLinks.start()
        self.cacheImages.start()
        self.cacheImageLock.start()
        self.joins = {}
        self.cache= {}
        self.cacheWelcomes.start()
        self.clearJoins.start()
        self.cacheSticky.start()

    @tasks.loop(minutes=100)
    async def cacheSticky(self):
        getStickys = self.sticky.find({})
        guilds_ids = []
        messages = []
        channels = []
        for i in await getStickys.to_list(length=999999):
            get_guilds = i['guild_id']
            get_messages = i['message']
            get_channels = i['channel']
            guilds_ids.append(get_guilds)
            messages.append(get_messages)
            channels.append(get_channels)
        self.stickycache = {channels: {'guild_id': guilds_ids, 'messages': messages}for (channels, guild_ids, messages) in zip(channels, guilds_ids, messages)}
        print(self.stickycache)

    @cacheSticky.before_loop
    async def before_cacheSticky(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=50)
    async def cacheWelcomes(self):
        getWelcomes = self.db.find({})
        guild_ids = []
        messages = []
        channels = []
        wlcs = []
        delete_afters = []
        for i in await getWelcomes.to_list(length=999):
            get_guilds = i['guild_id']
            get_messages = i['message']
            get_channels = i['channel']
            get_welc = i['welcome']
            get_deletions = i['delete_after']
            guild_ids.append(get_guilds)
            messages.append(get_messages)
            channels.append(get_channels)
            wlcs.append(get_welc)
            delete_afters.append(get_deletions)
        self.cache = {guild_ids: {'message': messages, 'channel': channels, 'welcome': wlcs, 'delete_after': delete_afters} for (guild_ids, messages, channels, wlcs, delete_afters) in zip(guild_ids, messages, channels, wlcs, delete_afters)}

    @cacheWelcomes.before_loop
    async def before_cacheWelcomes(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=40)
    async def clearJoins(self):
        try:
            self.joins.clear()
        except:
            pass; return

    @clearJoins.before_loop
    async def before_clearJoins(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=100)
    async def cacheImageLock(self):
        getImageLocks= self.imagelock.find({})
        guild_ids = []
        channels = []
        for i in await getImageLocks.to_list(length=99999):
            get_guilds = i['guild_id']
            get_channels = i['channel']
            guild_ids.append(get_guilds)
            channels.append(get_channels)
        self.imagelockcache = {guild_ids: {'channel': channels} for (guild_ids, channels) in zip(guild_ids, channels)}
        print(f'imagelock -> {self.imagelockcache}')

    @cacheImageLock.before_loop
    async def before_cacheImageLock(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=100)
    async def cacheImages(self):
        getImages= self.image.find({})
        guild_ids = []
        channels = []
        for i in await getImages.to_list(length=99999):
            get_guilds = i['guild_id']
            get_channels = i['channel']
            guild_ids.append(get_guilds)
            channels.append(get_channels)
        self.imagecache = {guild_ids: {'channel': channels} for (guild_ids, channels) in zip(guild_ids, channels)}
        print(f'imgcache -> {self.imagecache}')

    @cacheImages.before_loop
    async def before_cacheImages(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=100)
    async def cacheInvites(self):
        getInvites = self.invites.find({})
        guild_ids = []
        channels = []
        for i in await getInvites.to_list(length=99999):
            get_guilds = i['guild_id']
            get_channels = i['channel']
            guild_ids.append(get_guilds)
            channels.append(get_channels)
        self.invitescache = {guild_ids: {'channel': channels} for (guild_ids, channels) in zip(guild_ids, channels)}
        print(f'invite cache -> {self.invitescache}')

    @cacheInvites.before_loop
    async def before_cacheInvites(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=100)
    async def cacheLinks(self):
        getLinks = self.links.find({})
        guild_ids = []
        channels = []
        for i in await getLinks.to_list(length=99999):
            get_guilds = i['guild_id']
            get_channels = i['channel']
            guild_ids.append(get_guilds)
            channels.append(get_channels)
        self.linkscache = {guild_ids: {'channel': channels} for (guild_ids, channels) in zip(guild_ids, channels)}
        print(f'link cache -> {self.linkscache}') 

    @cacheLinks.before_loop
    async def before_cacheLinks(self):
        await self.bot.wait_until_ready()

    @commands.group(
        usage = 'manage_messages',
        description = 'Modify your servers settings',
        brief = 'subcommand',
        help = '```Syntax: settings <subcommand>\nExample: settings filter```'
    )
    async def settings(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                return await utils.send_command_help(ctx)
        except Exception as e:
            print(e)
    
    @settings.group(
        usage = 'manage_messages',
        description = 'Create certain filters such as images, links, invites etc.. for specified channels ',
        brief = 'subcommand',
        help = "```Syntax: settings filter <subcommand>\nExample: settings filter images```"
    )
    async def filter(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                return await utils.send_command_help(ctx)
        except Exception as e:
            print(e)

    @filter.command(
        aliases = ['img', 'settings'],
        usage = 'manage_messages',
        description = 'Filter images from being sent in specified channels ',
        brief = 'channel',
        help = "```Syntax: settings filter images [channel]\nExample: settings filter images #general```"
    )
    @commands.has_permissions(manage_channels=True)
    async def images(self, ctx, channel: discord.TextChannel, flags: Flags=None):
        check = await self.image.find_one({'guild_id': ctx.guild.id})
        if check and channel.id in check['channel']:
            await self.image.delete_many({'guild_id': ctx.guild.id})
            self.cacheImages.restart()
            return await utils.send_blurple(ctx, f"The channel: {channel.mention} will no longer be ``filtered`` for images.")
        
        else:
            await utils.send_blurple(ctx, f"Images will now be ``filtered`` in {channel.mention}")
            await self.image.insert_one({'guild_id': ctx.guild.id, 'channel': [channel.id], 'settings': 'enabled', 'punishment': 'mute'})
            self.cacheImages.restart()


    @filter.command(
        usage = 'manage_messages',
        description = 'Lock a channel to post images only',
        brief = 'channel',
        help = "```Syntax: settings filter imagelock [channel]]\nExample: settings filter imagelock #icons```"
    )
    @commands.has_permissions(manage_channels=True)
    async def imagelock(self, ctx, channel: discord.TextChannel, flags: Flags=None):
        check = await self.imagelock.find_one({'guild_id': ctx.guild.id})
        if check and channel.id in check['channel']:
            await self.imagelock.delete_many({'guild_id': ctx.guild.id})
            self.cacheImageLock.restart()
            return await utils.send_blurple(ctx, f"{channel.mention} is no longer locked for images.")
        else:
            await utils.send_blurple(ctx, f"{channel.mention} will now be locked to ``images`` only.")
            await self.imagelock.insert_one({'guild_id': ctx.guild.id, 'channel': [channel.id], 'settings': 'enabled', 'punishment': 'mute'})
            self.cacheImageLock.restart()

    @settings.command(
        name = 'imagelock',
        usage = 'manage_messages',
        description = 'Lock a channel to post images only',
        brief = 'channel',
        help = "```Syntax: settings imagelock [channel]]\nExample: settings imagelock #icons```"
    )
    @commands.has_permissions(manage_channels=True)
    async def imageloc(self, ctx, channel: discord.TextChannel, flags: Flags=None):
        check = await self.imagelock.find_one({'guild_id': ctx.guild.id})
        if check and channel.id in check['channel']:
            await self.imagelock.delete_many({'guild_id': ctx.guild.id})
            self.cacheImageLock.restart()
            return await utils.send_blurple(ctx, f"{channel.mention} is no longer locked for images.")
        else:
            await utils.send_blurple(ctx, f"{channel.mention} will now be locked to ``images`` only.")
            await self.imagelock.insert_one({'guild_id': ctx.guild.id, 'channel': [channel.id], 'settings': 'enabled', 'punishment': 'mute'})
            self.cacheImageLock.restart()

    @filter.command(
        usage = 'manage_messages',
        description = 'Filter invites from being sent in certain channels',
        brief = 'channel',
        help = "```Syntax: settings filter invites [channel]\nExample: settings filter invites #general```"
    )
    @commands.has_permissions(manage_channels=True)
    async def invites(self, ctx, channel: discord.TextChannel, flags: Flags=None):
        check = await self.invites.find_one({'guild_id': ctx.guild.id})
        if check and channel.id in check['channel']:
            await self.invites.delete_many({'guild_id': ctx.guild.id})
            await utils.send_blurple(ctx, f"Invites will no longer be ``filtered`` in {channel.mention}")
            self.cacheInvites.restart()
        else:
            await utils.send_blurple(ctx, f"Invites will now be ``filtered`` in {channel.mention}")
            self.cacheInvites.restart()
            return await self.invites.insert_one({'guild_id': ctx.guild.id, 'channel': [channel.id], 'settings': 'enabled', 'punishment': 'mute'})

    @filter.command(
        usage = 'manage_messages',
        description = 'Filter links from being sent in certain channels',
        brief = 'channel',
        help = "```Syntax: settings filter links [channel]\nExample: settings filter links #general```"
    )
    @commands.has_permissions(manage_channels=True)
    async def links(self, ctx, channel: discord.TextChannel, flags: Flags=None):
        check = await self.links.find_one({'guild_id': ctx.guild.id})
        if check and channel.id in check['channel']:
            await self.links.delete_many({'guild_id': ctx.guild.id})
            self.cacheLinks.restart()
            return await utils.send_blurple(ctx, f"Links will no longer be ``filtered`` in {channel.mention}")
        else:
            await utils.send_blurple(ctx, f"Links will now be ``filtered`` in {channel.mention}")
            await self.links.insert_one({'guild_id': ctx.guild.id, 'channel': [channel.id], 'settings': 'enabled', 'punishment': 'mute'})
            self.cacheLinks.restart()

    @settings.group(
       usage = 'Manage_channels',
       description = "Create a welcome message for new members",
       brief = "channel, message",
       help = """```Syntax: settings welcome <subcommand>\nExample: settings welcome add```"""
    )
    async def welcome(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                return await utils.command_help(ctx)
        except Exception as e:
            print(e)

    @settings.group(
       usage = 'Manage_channels',
       description = "Module that allows you to persist a message to a specific channel after a new message is sent.",
       brief = "channel, message",
       help = """```Syntax: settings sticky <subcommand>\nExample: settings sticky add```"""
    )
    async def sticky(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                return await utils.command_help(ctx)
        except Exception as e:
            print(e)

    
    @sticky.command(
        name='add',
        aliases = ['create', 'new'],
        usage = 'manage_channels',
        description = 'Create a specific message that will be sent to a specific channel after a new message.',
        brief = 'channel, message',
        help = '```Syntax: settings sticky add [channel] [message]\nExample: settings sticky add #support Please state your issue.```'
    )
    async def sticky_add(self, ctx, channel: discord.TextChannel, *, message):
        check = await self.sticky.find_one({ "guild_id": ctx.guild.id, 'channel': channel.id})
        if check:
            return await utils.send_issue(ctx, f"There is already an existing sticky message for the channel: {channel.mention}")
        else:
            await self.sticky.insert_one({
                'guild_id': ctx.guild.id,
                'channel': channel.id,
                'message': f'{message}'
            })
            self.cacheSticky.restart()
            return await utils.send_blurple(ctx, f"Successfully created sticky message.\n__Details:__\n```ruby\nChannel: {channel.id}\n\nMessage: {message}\n```")

    @sticky.command(
        name='remove',
        aliases = ['del', 'delete'],
        usage = 'manage_channels',
        description = 'Remove a stick message from a specified channel.',
        brief = 'channel',
        help = '```Syntax: settings sticky remove [channel]\nExample: settings sticky remove #support```'
    )
    async def sticky_remove(self, ctx, channel: discord.TextChannel):
        check = await self.sticky.find_one({ "guild_id": ctx.guild.id, 'channel': channel.id})
        if check:
            await self.sticky.delete_one({ "guild_id": ctx.guild.id, 'channel': channel.id})
            self.cacheSticky.restart()
            return await utils.send_issue(ctx, f"Removed sticky message for: {channel.mention}")
        else:
            return await utils.send_issue(ctx, f"There is no sticky message set for: {channel.mention}")

    @sticky.command(
        name='view',
        aliases = ['list'],
        usage = 'manage_channels',
        description = 'View the sticky messages in your server',
        brief = 'None',
        help = '```Example: settings sticky view```'
    )
    async def sticky_view(self, ctx):
        check = await self.sticky.find_one({ "guild_id": ctx.guild.id})
        if check:
            check_existing = self.sticky.find({ "guild_id": ctx.guild.id})
            messages = []
            channels = []
            for i in await check_existing.to_list(length=999999):
                get_messages = i['message']
                get_channels = i['channel']
                messages.append(get_messages)
                channels.append(get_channels)
            resp = [f"```ruby\nChannel: {channels}\nMessage: {messages}\n```\n{self.bot.get_channel(channels).mention}" for channels, messages in zip(channels, messages)]
            embeds = []
            for count, i in enumerate(resp, start=1):
                embed = discord.Embed(timestamp=ctx.message.created_at, color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                embed.set_author(name=f"Sticky messages in {ctx.guild.name}", icon_url=ctx.author.display_avatar.url)
                embed.set_thumbnail(url=ctx.guild.icon.url)
                embed.description = f"``{count}.)`` **{i}**"
                embeds.append(embed)
                embed.set_footer(text=f"Pages: {len(embeds)}/{len(messages)}")
            paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
            if len(embeds) > 1:
                paginator.add_button('prev', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.blurple)
                paginator.add_button('next', emoji='<:right:934237462660788304>', style=discord.ButtonStyle.blurple)
            return await paginator.start()
        else:
            return await utils.send_issue(ctx, 'No sticky messages exist in this server!')
            


    
    @welcome.command(
       usage = 'Manage_channels',
       description = "Modify or create a welcome message for new members to a specified channel",
       brief = "message",
       help = """```Syntax: settings welcome add [channel] [message]\nExample: settings welcome add #welcome Hey {user.mention}```"""
    )
    @commands.has_permissions(manage_channels=True)
    async def add(self, ctx, channel: discord.TextChannel, *, message):
        async with ctx.typing():
            params = message
            user = ctx.author
            try:
                    if message == None:
                        await utils.send_command_help(ctx)
                    if not message.startswith("(embed)"):
                        check = await self.db.count_documents({ "guild_id": ctx.guild.id })
                        if check > 1:
                            return await utils.send_issue(ctx, "To add multiple welcomes you must have :star: (Premium)[https://blame.gg/discord]")
                        if not check:
                            await self.db.insert_one({
                                "guild_id": ctx.guild.id,
                                #"type": None,
                                "message": f"{message}",
                                "channel": channel.id,
                                "welcome": 'Enabled',
                                "delete_after": None
                            })
                            self.cacheWelcomes.restart()
                            await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {user.mention}: Your **welcome message** has been **set** to:\n```{message}```\nChannel set to: {channel.mention}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                        else:
                            return await utils.send_issue(ctx, "To add multiple welcomes you must have :star: [Premium](https://blame.gg/discord)")
                    elif message:
                        check = await self.db.count_documents({ "guild_id": ctx.guild.id })
                        if check > 1:
                            return await utils.send_issue(ctx, "To add multiple welcomes you must have :star: [Premium](https://blame.gg/discord")
                        if not check:
                            await self.db.insert_one({
                                "guild_id": ctx.guild.id,
                                #"type": None,
                                "message": None,
                                "channel": None,
                                "welcome": 'Disabled',
                                "delete_after": None
                            })
                            await asyncio.sleep(1)
                            params = params.replace('(embed)', '')
                            params = await utils.test_vars(ctx, user, params)
                            em = await utils.to_embed(ctx, params)
                            try:
                                await ctx.send(content=f"This is an example ``(try {ctx.prefix}welcome test for more detailed example)``:", embed=em)
                            except Exception as e:
                                await ctx.send(f"```{e}```")
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "message": str(message)}})
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "welcome": "Enabled"}})
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "channel": channel.id}})
                            self.cacheWelcomes.restart()
                            await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {user.mention}: Your **welcome message** has been **set** to:\n```\n{message}\n```\nChannel set to: {channel.mention}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                        else:
                            #params = params.replace('(embed)', '')
                            #params = await utils.test_vars(ctx, user, params)
                           # em = await utils.to_embed(ctx, params)
                           # try:
                             #   await ctx.send(content="This is an example:", embed=em)
                            #except Exception as e:
                              #  await ctx.send(f"```{e}```")
                            return await utils.send_issue(ctx, "To add multiple welcomes you must have :star: [Premium](https://blame.gg/discord)")
            except Exception as e:
                fail = discord.Embed(description=f"```{e}```", color=self.urgecolor)
                return await ctx.send(embed=fail)

    @welcome.command(
        aliases = ['disable'],
        usage = "manage_channels",
        description = "Remove your welcome settings **([1 without :star: Premium](https://blame.gg/discord))**",
        brief = "None",
        help = "```Example: settings welcome remove```"
    )
    @commands.has_permissions(manage_channels=True)
    async def remove(self, ctx):
        check = await self.db.find_one({'guild_id': ctx.guild.id})
        if check:
            await utils.send_blurple(ctx, f"Welcome removed for <#{check['channel']}>")
            self.cacheWelcomes.restart()
            return await self.db.delete_one({'guild_id': ctx.guild.id})
        else:
            return await utils.send_issue(ctx, f'No welcomes have been added through ``{ctx.prefx}welcome settings add``')


    @welcome.command(
        aliases = ['view'],
        name='test',
        usage = "Manage_channels",
        description = "View your welcome message with its exact syntax",
        brief = "None",
        help = "```Example: settings welcome test```"
    )
    @commands.has_permissions(manage_channels=True)
    async def testt(self, ctx):
        user = ctx.author
        async with ctx.typing():
            try:
                data = await self.db.find_one({"guild_id": ctx.guild.id})
                if data:
                    message = data['message']
                    if message == None:
                        notFound = discord.Embed(description=f"{self.urgentmoji} No **welcome message** has been set. Please create one and **retry**.", color=self.urgecolor)
                        return await ctx.send(embed=notFound)
                    channel = data['channel']
                    if channel == None:
                        notFound2 = discord.Embed(description=f"{self.urgentmoji} No **welcome channel** has been set. Please create one and **retry**.", color=self.urgecolor)
                        return await ctx.send(embed=notFound2)
                    user = ctx.author
                    channel2=self.bot.get_channel(channel)
                    if not channel2:
                        return
        
                    if message.startswith("(embed)"):
                        message = message.replace('(embed)', '')
                        message = await utils.test_vars(ctx, user, params=message)
                        if "content:" in message.lower():
                            em = await utils.to_embed(ctx, params=message)
                            msg = await utils.to_content(ctx, params=message)
                            print('a')
                            try:
                                await channel2.send(content=msg, embed=em)
                            except Exception as e:
                                await ctx.send(f"```{e}```")
                            #await channel2.send(embed=em)
                            await ctx.send(f":thumbsup: {channel2.mention}")
                        else:
                            em = await utils.to_embed(ctx, params=message)
                            try:
                                await channel2.send(embed=em)
                            except Exception as e:
                                await ctx.send(f"```{e}```")
                            #await channel2.send(embed=em)
                            await ctx.send(f":thumbsup: {channel2.mention}")
                    else:
                        message = await utils.test_vars(ctx, user, params=message)
                        await channel2.send(message)
                        await ctx.send(f":thumbsup: {channel2.mention}")
                else:
                    notFound = discord.Embed(description=f"{self.urgentmoji} **No welcome structures were found for this guild...**", color=self.urgecolor)
                    return await ctx.send(embed=notFound)
            except Exception as e:
                print(e)

    @welcome.command(
        name='variables',
        usage = "Manage_channels",
        description = "View all accepted variables for the welcome message",
        brief = "None",
        help = "```Example: settings welcome variables```"
    )
    async def variabless(self, ctx):
        async with ctx.typing():
            try:
                embed=discord.Embed(description="**https://docs.blame.gg/table-of-contents/embeds**", color=0x2F3136)
                embed.set_image(url="https://cdn.discordapp.com/attachments/851633587915587615/1018670211878101052/1662939809510_1662939608800_0_Screenshot_2022-09-11_193705_FAST_x2.png")
                await ctx.send(embed=embed)
            except Exception as e:
                fail = discord.Embed(description=f"```{e}```", color=self.urgecolor)
                return await ctx.send(embed=fail)
    

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            urls = ['https', 'www', 'http', 'www']
            try: 
                check5 = self.stickycache[message.channel.id]
            except KeyError:
                pass; return
            if 'discord.gg' in message.content.lower():
                try:
                    check1 = self.invitescache[message.guild.id]
                except KeyError:
                    return
                if check1 and message.channel.id in check1['channel'] and not message.author.guild_permissions.manage_messages:
                    return await message.delete()
            if 'https' in message.content.lower() or 'http' in message.content.lower() or 'www' in message.content.lower():
                try:
                    check2= self.linkscache[message.guild.id]
                except KeyError:
                    return
                if check2 and message.channel.id in check2['channel'] and not message.author.guild_permissions.manage_messages:
                    return await message.delete()
            if message.attachments:
                try:
                    check3 = self.imagecache[message.guild.id]
                except KeyError:
                    return
                if check3 and message.channel.id in check3['channel'] and not message.author.guild_permissions.manage_messages:
                    return await message.delete()
            if not message.attachments:
                try:
                    check4 = self.imagelockcache[message.guild.id]
                except KeyError:
                    return 
                if check4 and message.channel.id in check4['channel'] and not message.author.guild_permissions.manage_messages:
                    return await message.delete()
            if check5:
                print('a')
                messagee = check5['messages']
                if messagee.startswith("(embed)"):
                    messagee = messagee.replace('(embed)', '')
                    messagee = await utils.welcome_vars(user=message.author, params=messagee)
                    if "content:" in messagee.lower():
                        em = await utils.to_embed(ctx, params=messagee)
                        msg = await utils.to_content(ctx, params=messagee)
                        try:
                            return await self.bot.get_channel(check5).send(content=msg, embed=em)
                        except Exception as e:
                            print(f'{e} real')
                    else:
                        messagee = messagee.replace('(embed)', '')
                        messagee = await utils.welcome_vars(user=message.author, params=messagee)
                        em = await utils.to_embed(ctx, params=messagee)
                        try:
                            return await self.bot.get_channel(check5).send(eHmbed=em)
                        except Exception as e:
                            print(f'{e} real')
                if not messagee.startswith("(embed)"):
                    messagee = await utils.welcome_vars(user=message.author, params=messagee)
                    return await self.bot.get_channel(check5).send(messagee)

            else:
                return
        except Exception as e:
            print(e)    

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            data = self.cache[member.guild.id]
        except KeyError:
            return
        try:
            self.joins[member.guild.id]
        except KeyError:
            self.joins[member.guild.id] =1
        guild = self.joins[member.guild.id]
        self.joins[member.guild.id] = self.joins[member.guild.id]+1
        print(self.joins)
        try:
            if data and not self.joins[member.guild.id] >= 7:
                chan = data['channel']
                message = data['message']
                dele = data['delete_after']
                if chan == None:
                    return
                if message == None:
                    return
                data = await self.db.find_one({"guild_id": member.guild.id})
                chan = data['channel']
                message = data['message']
                dele = data['delete_after']
                ctx=member.guild.get_member(member)

                if message.startswith("(embed)") and dele == None:
                    message = message.replace('(embed)', '')
                    message = await utils.welcome_vars(user=member, params=message)
                    if "content:" in message.lower():
                        em = await utils.to_embed(ctx, params=message)
                        msg = await utils.to_content(ctx, params=message)
                        try:
                            return await self.bot.get_channel(chan).send(content=msg, embed=em)
                        except Exception as e:
                            print(e)
                    else:
                        message = message.replace('(embed)', '')
                        message = await utils.welcome_vars(user=member, params=message)
                        em = await utils.to_embed(ctx, params=message)
                        try:
                            return await self.bot.get_channel(chan).send(embed=em)
                        except Exception as e:
                            print(e)
                elif message.startswith("(embed)"):
                    message = message.replace('(embed)', '')
                    message = await utils.welcome_vars(user=member, params=message)
                    if "content:" in message.lower():
                        em = await utils.to_embed(ctx, params=message)
                        msg = await utils.to_content(ctx, params=message)
                        try:
                            return await self.bot.get_channel(chan).send(content=msg, embed=em, delete_after=dele)
                        except Exception as e:
                            print(e)
                    else:
                        message = message.replace('(embed)', '')
                        message = await utils.welcome_vars(user=member, params=message)
                        em = await utils.to_embed(ctx, params=message)
                        try:
                            return await self.bot.get_channel(chan).send(embed=em, delete_after=dele)
                        except Exception as e:
                            print(e)
                if not message.startswith("(embed)") and dele == None:
                    message = await utils.welcome_vars(user=member, params=message)
                    await self.bot.get_channel(chan).send(message)
                elif not message.startswith("(embed)"):
                    message = await utils.welcome_vars(user=member, params=message)
                    await self.bot.get_channel(chan).send(message, delete_after=dele)
            else:
                return
                pass
        except:
            pass
    
    @settings.command(
        aliases = ['banmsg', 'invokebanmsg'],
        description = 'Set the message that the bot will send upon banning someone',
        brief = 'message',
        usage = 'manage_guild',
        help = '```Syntax: settings banmessage [message]\nExample: settings banmessage :goat:```'
    )
    @commands.has_permissions(manage_guild=True)
    async def ban_msg(self, ctx, *, message):
        check = await self.bans.find_one({'guild_id': ctx.guild.id})
        if check:
            await self.bans.update_one({ "guild_id": ctx.guild.id }, { "$set": { "banmsg": f"{message}"}})
            return await utils.send_blurple(ctx, f"Ban message has been updated to:\n```{message}```")
        else:
            await self.bans.insert_one({
                'guild_id': ctx.guild.id,
                "banmsg": f"{message}"
            })
            return await utils.send_blurple(ctx, f"Ban message has been set to:\n```{message}```")

    @commands.command(
        name='banmessage',
        aliases = ['banmsg', 'invokebanmsg'],
        description = 'Set the message that the bot will send upon banning someone',
        brief = 'message',
        usage = 'manage_guild',
        help = '```Syntax: banmessage [message]\nExample: banmessage :goat:```'
    )
    @commands.has_permissions(manage_guild=True)
    async def ban_message(self, ctx, *, message):
        check = await self.bans.find_one({'guild_id': ctx.guild.id})
        if check:
            await self.bans.update_one({ "guild_id": ctx.guild.id }, { "$set": { "banmsg": f"{message}"}})
            return await utils.send_blurple(ctx, f"Ban message has been updated to:\n```{message}```")
        else:
            await self.bans.insert_one({
                'guild_id': ctx.guild.id,
                "banmsg": f"{message}"
            })
            return await utils.send_blurple(ctx, f"Ban message has been set to:\n```{message}```")




async def setup(bot):
    await bot.add_cog(serversettings(bot))         

