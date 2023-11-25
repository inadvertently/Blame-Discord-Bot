import discord, asyncio, typing, re, httpx, motor.motor_asyncio, json, Core.confirm as cop_is_gae
from typing import Optional
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType
from pendulum import time
import Core.help as help
import Core.utils as utils 
import random, shutil, tempfile, os
from colorama import Fore as f
from Core.utils import get_theme

def strip_codeblock(content):
    if content.startswith('```') and content.endswith('```'):
        return content.strip('```')
    return content.strip('` \n')


class Flags(commands.FlagConverter, prefix='--', delimiter=' ', case_insensitive=True):
    @classmethod
    async def convert(cls, ctx, argument: str):
        argument = strip_codeblock(argument).replace(' —', ' --')
        return await super().convert(ctx, argument)
    channel: discord.TextChannel = None
    message: str = None
    delete_after: int =None

class welcomeRR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db["welcome"]
        self.urgecolor = 0xF3DD6C
        self.errorcol = 0xA90F25 # error color
        self.success = discord.Colour.blurple() #theme
        self.checkmoji = "<:blurple_check:921544108252741723>" # success emoji
        self.xmoji = "<:yy_yno:921559254677200957>" # unsuccessful emoji
        self.urgentmoji = "<:n_:921559211366838282>" # exclamation emoji
        self.joins = {}
        self.cache= {}
        self.cacheWelcomes.start()
        self.clearJoins.start()

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
        print(f"{f.LIGHTRED_EX}[{f.RESET}{f.BLUE}(Loop Created){f.RESET}{f.LIGHTRED_EX}]{f.RESET} {f.GREEN}->{f.RESET} {f.LIGHTGREEN_EX}Welcome CACHE initiated.{f.RESET}")

    @commands.group(
    usage = "Manage_channels",
    description = "Create your own custom way of greeting new members to your server",
    brief = "subcommand, argument, subarg[Optional]",
    help = "```Syntax: welcome [subcommand] <argument> <subarg[Optional]>\nExample: welcome settings setup --mesage welcome to ther server```"
    )
    async def welcome(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Group Command: welcome settings", description="Create your own custom way of greeting new members to your server\n```Syntax: welcome settings <argument> <subarg[Optional]>\nExample: welcome settings remove```", color = discord.Color.blurple())
                embed.set_author(name="Welcome Settings help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('welcome').walk_commands()])} ・ Welcome Settings")
                return await ctx.send(embed=embed)
        except Exception as e:
            return


    @welcome.group(name='settings', description="welcome settings group", usage='Send Messages', help="```Example: ;welcome settings <subcommand>```")
    #@commands.cooldown(3, 14, BucketType.user)
    async def settings(self, ctx):
            try:
                check = await self.db.count_documents({ "guild_id": ctx.guild.id })
                if ctx.invoked_subcommand is None and check:
                    data = await self.db.find_one({"guild_id": ctx.guild.id})
                    Messageinfo = data['message']
                    channel = data['channel']
                    delete = data['delete_after']
                    resp = discord.Embed(title=":mag: Settings found..", description=f"""```json\nChannel: {channel}\n\n"Message": {Messageinfo}```""", color=discord.Color.blurple())
                    resp.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
                    resp.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
                    return await ctx.send(embed=resp)


                elif ctx.invoked_subcommand is None:
                    embed = discord.Embed(title="Group Command: welcome settings", description="Settings for the welcome module\n```Syntax: welcome settings [subcommand] <argument> <subarg[Optional]>\nExample: welcome settings setup --mesage heyyyy welcome```", color = discord.Color.blurple())
                    embed.set_author(name="Welcome help", icon_url=ctx.me.avatar.url)
                    embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('welcome').walk_commands()])} ・ Welcome")
                    return await ctx.send(embed=embed)
            except Exception as e:
                return


    @settings.command(
        usage = "Manage_channels",
        description= "The command responsible for bulding you guild's welcome structure in our database.",
        brief = "flags.channel, flags.message",
        help = """```Syntax: welcome settings setup --channel [channel] --message [message]\n\nExample: welcome settings setup --channel #general --message (embed)(description: welcome {user.mention})$v(color: F3136) --delete_after 10```"""
    )
    @commands.has_permissions(manage_channels=True)
    #@commands.cooldown(3, 14, BucketType.user)
    async def setup(self, ctx, *, flags: Flags):
        async with ctx.typing():
            try:
                check = await self.db.count_documents({ "guild_id": ctx.guild.id })
                if flags.channel == None:
                    flags.channel = ctx.channel
                #await ctx.send(f"Channel: {flags.channel.mention}")
                if flags.message == None:
                    await utils.send_command_help(ctx)
                
                if not flags.message.startswith("{") and not check:
                    await self.db.insert_one({
                        "guild_id": ctx.guild.id,
                        #"type": None,
                        "message": None,
                        "channel": None,
                        "welcome": 'Disabled',
                        "delete_after": None
                    })
                    final = discord.Embed(description="<:check:921544057312915498> **__The welcome module has successfully been built for this guild__**", timestamp=ctx.message.created_at, color= 0x43B581)
                    final.add_field(name="Structure:", value=f"""```json\n"Channel": {flags.channel.mention}\n"Message": "{flags.message}"```""")
                    final.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
                    final.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
                    await asyncio.sleep(1.5)
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "welcome": "Enabled"}})
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "channel": flags.channel.id}})
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "message": str(flags.message)}})
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "delete_after": flags.delete_after}})
                    await ctx.send(embed=final)
                    self.cacheWelcomes.restart()
                if not flags.message.startswith("{") and check:
                    final = discord.Embed(description="<:check:921544057312915498> **__The welcome module has successfully been built for this guild__**", timestamp=ctx.message.created_at, color= 0x43B581)
                    final.add_field(name="Structure:", value=f"""```json\n"Channel": {flags.channel.mention}\n"Message": "{flags.message}"```""")
                    final.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
                    final.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
                    await asyncio.sleep(1.5)
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "welcome": "Enabled"}})
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "channel": flags.channel.id}})
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "message": str(flags.message)}})
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "delete_after": flags.delete_after}})
                    await ctx.send(embed=final)
                    self.cacheWelcomes.restart()

                if flags.message.startswith("{") and not check:
                    try:
                        res = json.loads(flags.message)
                        em = discord.Embed().from_dict(res)
                    except json.decoder.JSONDecodeError:
                        return await ctx.send("**The message you inputted is not valid, here are some things to check:**\n\n**1.** All name/value pairs are wrapped in double quotes.\n**2.** Your objects are seperated by commas.\n**3.** Message object should be wrapped in curly braces ``{}``.\n**4. **Need more help? Join the discord @ https://blame.gg/discord or use an embed builder @ https://rival.rocks/embedbuilder/ ")
                    first = discord.Embed(description="<:check:921544057312915498> Beginning to build **welcome structure..**", color= 0x43B581)
                    firstsend = await ctx.send(embed=first)
                    await asyncio.sleep(1)
                    await self.db.insert_one({
                        "guild_id": ctx.guild.id,
                        #"type": None,
                        "message": None,
                        "channel": None,
                        "welcome": 'Disabled',
                        "delete_after": None
                    })
                    ls = ['1', '2', '3', '4', '5', '6']
                    second = discord.Embed(description=f"{self.urgentmoji} **Built ``{random.choice(ls)}/12`` structures... **", color=self.urgecolor)
                    await asyncio.sleep(1)
                    await firstsend.edit(embed=second)
                    third = discord.Embed(description=":mag: **Looking for previous welcome indexes..**", color=discord.Color.blurple())
                    await asyncio.sleep(1.2)
                    await firstsend.edit(embed=third)
                    bfinal = discord.Embed(description=f"{self.urgentmoji} **12/12** structures built.. \n```[{flags.channel}, {flags.message}, {ctx.guild.id}...]```", color= self.urgecolor)
                    await asyncio.sleep(1.3)
                    await firstsend.edit(embed=bfinal)
                    final = discord.Embed(description="<:check:921544057312915498> **__The welcome module has successfully been built for this guild__**", timestamp=ctx.message.created_at, color= 0x43B581)
                    final.add_field(name="Structure:", value=f"""```json\n"Channel": {flags.channel.mention}\n"Message": "{flags.message}"```""")
                    final.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
                    final.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
                    await asyncio.sleep(1.5)
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "welcome": "Enabled"}})
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "channel": flags.channel.id}})
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "message": str(flags.message)}})
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "delete_after": flags.delete_after}})
                    await firstsend.edit(embed=final)
                    self.cacheWelcomes.restart()
                if flags.message.startswith("{") and check:
                    try:
                        res = json.loads(flags.message)
                        em = discord.Embed().from_dict(res)
                    except json.decoder.JSONDecodeError:
                        return await ctx.send("**The message you inputted is not valid, here are some things to check:**\n\n**1.** All name/value pairs are wrapped in double quotes.\n**2.** Your objects are seperated by commas.\n**3.** Message object should be wrapped in curly braces ``{}``.\n**4. **Need more help? Join the discord @ https://blame.gg/discord or use an embed builder @ https://rival.rocks/embedbuilder/ ")
                    first = discord.Embed(description="<:check:921544057312915498> Beginning to build **welcome structure..**", color= 0x43B581)
                    firstsend = await ctx.send(embed=first)
                    await asyncio.sleep(1)
                    ls = ['1', '2', '3', '4', '5', '6']
                    second = discord.Embed(description=f"{self.urgentmoji} **Built ``{random.choice(ls)}/12`` structures... **", color=self.urgecolor)
                    await asyncio.sleep(1)
                    await firstsend.edit(embed=second)
                    third = discord.Embed(description=":mag: **Looking for previous welcome indexes..**", color=discord.Color.blurple())
                    await asyncio.sleep(1.2)
                    await firstsend.edit(embed=third)
                    bfinal = discord.Embed(description=f"{self.urgentmoji} **12/12** structures built.. \n```[{flags.channel}, {flags.message}, {ctx.guild.id}...]```", color= self.urgecolor)
                    await asyncio.sleep(1.3)
                    await firstsend.edit(embed=bfinal)
                    final = discord.Embed(description="<:check:921544057312915498> **__The welcome module has successfully been built for this guild__**", timestamp=ctx.message.created_at, color= 0x43B581)
                    final.add_field(name="Structure:", value=f"""```json\n"Channel": {flags.channel.mention}\n"Message": "{flags.message}"```""")
                    final.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
                    final.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
                    await asyncio.sleep(1.5)
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "welcome": "Enabled"}})
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "channel": flags.channel.id}})
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "message": str(flags.message)}})
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "delete_after": flags.delete_after}})
                    await firstsend.edit(embed=final)
                    self.cacheWelcomes.restart()
            except Exception as e:
                fail = discord.Embed(description=f"```{e}```", color=self.urgecolor)
                return await ctx.send(embed=fail)

    @welcome.command(
        name='test',
        usage = "Manage_channels",
        description = "View your welcome message with its exact syntax",
        brief = "None",
        help = "```Example: welcome test```"
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
                return


    @settings.command(
        usage = "Manage_channels",
        description = "View your welcome message with its exact syntax",
        brief = "None",
        help = "```Example: welcome test```"
    )
    @commands.has_permissions(manage_channels=True)
    async def test(self, ctx):
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
                return

    @settings.command(
        aliases = ['variables'],
        usage = "Manage_channels",
        description = "View all accepted variables for the welcome message",
        brief = "None",
        help = "```Example: welcome settings variables```"
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

    @commands.command(
        usage = "Manage_channels",
        description = "View all accepted variables for the welcome message",
        brief = "None",
        help = "```Example: welcome settings variables```"
    )
    async def variables(self, ctx):
        async with ctx.typing():
            try:
                embed=discord.Embed(description="**https://docs.blame.gg/table-of-contents/embeds**", color=0x2F3136)
                embed.set_image(url="https://cdn.discordapp.com/attachments/851633587915587615/1018670211878101052/1662939809510_1662939608800_0_Screenshot_2022-09-11_193705_FAST_x2.png")
                await ctx.send(embed=embed)
            except Exception as e:
                fail = discord.Embed(description=f"```{e}```", color=self.urgecolor)
                return await ctx.send(embed=fail)


    @settings.command(
        aliases = ['disable'],
        usage = "Manage_channels",
        description = "Remove your current welcome structure",
        brief = "None",
        help = "```Example: welcome remove```"
    )
    @commands.has_permissions(manage_channels=True)
    async def remove(self, ctx):
        async with ctx.typing():
            data = await self.db.find_one({"guild_id": ctx.guild.id})
            if not data:
                notFound = discord.Embed(description=f"{self.urgentmoji} **No welcome structures were found for this guild...**", color=self.urgecolor)
                return await ctx.send(embed=notFound)
            else:
                data2 = await self.db.find_one({"guild_id": ctx.guild.id})
                chan = data2["channel"]
                dele = data2['delete_after']
                msg = data2['message']
                found = discord.Embed(title="Are you sure you want to delete this welcome structure?", timestamp=ctx.message.created_at, color=self.errorcol)
                found.add_field(name=f"Channel:", value=f"<#{chan}>", inline=True)
                found.add_field(name=f"delete_after:", value=dele, inline=True)
                found.add_field(name=f"Message:", value=f"json\n```{msg}```", inline=False)
                found.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
                found.set_footer(text=f"{ctx.guild.name} ・ Structure: (1/1 structures)", icon_url=ctx.guild.icon.url)
                msg = await ctx.send(embed=found)

                async def confirm():
                    data2 = await self.db.find_one({"guild_id": ctx.guild.id})
                    mssg = data2['message']
                    await msg.edit(view=None, embed=discord.Embed(description=f"<:check:921544057312915498> **The welcome structure has been removed**\n\nFor future reference, here is the old message:\n```{mssg}```", color= 0x43B581))
                    await self.db.delete_many({ "guild_id": ctx.guild.id })
                    self.cacheWelcomes.restart()
                async def cancel():
                    await msg.edit(view=None, embed=discord.Embed(description=f"{self.urgentmoji} **Proccess cancelled**, your welcome structure has not been deleted ", color= self.urgecolor))
                confirmed:bool = await cop_is_gae.confirm(self, ctx, msg)
                if confirmed:
                    await confirm()
                else:
                    await cancel()
        
    @welcome.command(
        name='remove',
        aliases = ['disable'],
        usage = "Manage_channels",
        description = "Remove your current welcome structure",
        brief = "None",
        help = "```Example: welcome remove```"
    )
    @commands.has_permissions(manage_channels=True)
    async def removee(self, ctx):
        async with ctx.typing():
            data = await self.db.find_one({"guild_id": ctx.guild.id})
            if not data:
                notFound = discord.Embed(description=f"{self.urgentmoji} **No welcome structures were found for this guild...**", color=self.urgecolor)
                return await ctx.send(embed=notFound)
            else:
                data2 = await self.db.find_one({"guild_id": ctx.guild.id})
                chan = data2["channel"]
                dele = data2['delete_after']
                msg = data2['message']
                found = discord.Embed(title="Are you sure you want to delete this welcome structure?", timestamp=ctx.message.created_at, color=self.errorcol)
                found.add_field(name=f"Channel:", value=f"<#{chan}>", inline=True)
                found.add_field(name=f"delete_after:", value=dele, inline=True)
                found.add_field(name=f"Message:", value=f"json\n```{msg}```", inline=False)
                found.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
                found.set_footer(text=f"{ctx.guild.name} ・ Structure: (1/1 structures)", icon_url=ctx.guild.icon.url)
                msg = await ctx.send(embed=found)

                async def confirm():
                    data2 = await self.db.find_one({"guild_id": ctx.guild.id})
                    mssg = data2['message']
                    await msg.edit(view=None, embed=discord.Embed(description=f"<:check:921544057312915498> **The welcome structure has been removed**\n\nFor future reference, here is the old message:\n```{mssg}```", color= 0x43B581))
                    await self.db.delete_many({ "guild_id": ctx.guild.id })
                    self.cacheWelcomes.restart()
                async def cancel():
                    await msg.edit(view=None, embed=discord.Embed(description=f"{self.urgentmoji} **Proccess cancelled**, your welcome structure has not been deleted ", color= self.urgecolor))
                confirmed:bool = await cop_is_gae.confirm(self, ctx, msg)
                if confirmed:
                    await confirm()
                else:
                    await cancel()


    @settings.command(
        usage = "Manage_channels",
        description = "Set your welcome structures channel that the message will send to",
        brief = "channel",
        help = "```Syntax: welcome settings channel [channel]\nExample: welcome settings channel #general```"
    )
    @commands.has_permissions(manage_channels=True)
    async def channel(self, ctx, channel: discord.TextChannel=None):
        async with ctx.typing():
            try:
                if channel == None:
                    await utils.send_command_help(ctx)
                elif channel:
                    check = await self.db.count_documents({ "guild_id": ctx.guild.id })
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
                        await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "channel": channel.id}})
                        await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> **The welcome channel will now be** {channel.mention}", color = 0x43B581))
                        self.cacheWelcomes.restart()
                    else: 
                        await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "channel": channel.id}})
                        await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> **The welcome channel will now be** {channel.mention}", color = 0x43B581))
                        self.cacheWelcomes.restart()
            except Exception as e:
                fail = discord.Embed(description=f"```{e}```", color=self.urgecolor)
                return await ctx.send(embed=fail)

    @welcome.command(
        name = 'channel',
        usage = "Manage_channels",
        description = "Set your welcome structures channel that the message will send to",
        brief = "channel",
        help = "```Syntax: welcome channel [channel]\nExample: welcome channel #general```"
    )
    @commands.has_permissions(manage_channels=True)
    async def channell(self, ctx, channel: discord.TextChannel=None):
        async with ctx.typing():
            try:
                if channel == None:
                    await utils.send_command_help(ctx)
                elif channel:
                    check = await self.db.count_documents({ "guild_id": ctx.guild.id })
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
                        await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "channel": channel.id}})
                        await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> **The welcome channel will now be** {channel.mention}", color = 0x43B581))
                        self.cacheWelcomes.restart()
                    else: 
                        await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "channel": channel.id}})
                        await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> **The welcome channel will now be** {channel.mention}", color = 0x43B581))
                        self.cacheWelcomes.restart()
            except Exception as e:
                fail = discord.Embed(description=f"```{e}```", color=self.urgecolor)
                return await ctx.send(embed=fail)


    @settings.command(
       usage = 'Manage_channels',
       description = "Change your welcome structures message (Accepts our format or plain tex)",
       brief = "message",
       help = """```Syntax: welcome settings message [message]\nJSON Example: welcome settings message (embed)(description: welcome {user.mention})$v(color: F3136)\nPlainTxt Example: welcome settings message welcome {user.mention}```"""
    )
    @commands.has_permissions(manage_channels=True)
    async def message(self, ctx, *, message=None):
        async with ctx.typing():
            params = message
            user = ctx.author
            try:
                    if message == None:
                        await utils.send_command_help(ctx)
                    if not message.startswith("(embed)"):
                        check = await self.db.count_documents({ "guild_id": ctx.guild.id })
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
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "message": str(message)}})
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "welcome": "Enabled"}})
                            await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {user.mention}: Your **welcome message** has been **set** to:\n```{message}```", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                            self.cacheWelcomes.restart()
                        else:
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "welcome": "Enabled"}})
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "message": str(message)}})
                            await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {user.mention}: Your **welcome message** has been **updated** to:\n```{message}```", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                            self.cacheWelcomes.restart()
                    elif message:
                        check = await self.db.count_documents({ "guild_id": ctx.guild.id })
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
                                await ctx.send(content=f"This is an example ``(try {ctx.prefix}welcome test for mor detailed example)``:", embed=em)
                            except Exception as e:
                                await ctx.send(f"```{e}```")
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "message": str(message)}})
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "welcome": "Enabled"}})
                            await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {user.mention}: Your **welcome message** has been **set** to:\n```\n{message}\n```", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                            self.cacheWelcomes.restart()
                        else:
                            params = params.replace('(embed)', '')
                            params = await utils.test_vars(ctx, user, params)
                            em = await utils.to_embed(ctx, params)
                            try:
                                await ctx.send(content="This is an example example:", embed=em)
                            except Exception as e:
                                await ctx.send(f"```{e}```")
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "welcome": "Enabled"}})
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "message": str(message)}})
                            await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {user.mention}: Your **welcome message** has been **updated** to:\n```\n{message}\n```", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                            self.cacheWelcomes.restart()
            except Exception as e:
                fail = discord.Embed(description=f"```{e}```", color=self.urgecolor)
                return await ctx.send(embed=fail)

    @welcome.command(
        name='message',
       usage = 'Manage_channels',
       description = "Change your welcome structures message (Accepts our format or plain tex)",
       brief = "message",
       help = """```Syntax: welcome  message [message]\nJSON Example: welcome message (embed)(description: welcome {user.mention})$v(color: F3136)\nPlainTxt Example: welcome message welcome {user.mention}```"""
    )
    @commands.has_permissions(manage_channels=True)
    async def messagee(self, ctx, *, message=None):
        async with ctx.typing():
            params = message
            user = ctx.author
            try:
                    if message == None:
                        await utils.send_command_help(ctx)
                    if not message.startswith("(embed)"):
                        check = await self.db.count_documents({ "guild_id": ctx.guild.id })
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
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "message": str(message)}})
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "welcome": "Enabled"}})
                            await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {user.mention}: Your **welcome message** has been **set** to:\n```{message}```", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                            self.cacheWelcomes.restart()
                        else:
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "welcome": "Enabled"}})
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "message": str(message)}})
                            await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {user.mention}: Your **welcome message** has been **updated** to:\n```{message}```", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                            self.cacheWelcomes.restart()
                    elif message:
                        check = await self.db.count_documents({ "guild_id": ctx.guild.id })
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
                                await ctx.send(content=f"This is an example ``(try {ctx.prefix}welcome test for mor detailed example)``:", embed=em)
                            except Exception as e:
                                await ctx.send(f"```{e}```")
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "message": str(message)}})
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "welcome": "Enabled"}})
                            await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {user.mention}: Your **welcome message** has been **set** to:\n```\n{message}\n```", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                            self.cacheWelcomes.restart()
                        else:
                            params = params.replace('(embed)', '')
                            params = await utils.test_vars(ctx, user, params)
                            em = await utils.to_embed(ctx, params)
                            try:
                                await ctx.send(content="This is an example example:", embed=em)
                            except Exception as e:
                                await ctx.send(f"```{e}```")
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "welcome": "Enabled"}})
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "message": str(message)}})
                            await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {user.mention}: Your **welcome message** has been **updated** to:\n```\n{message}\n```", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                            self.cacheWelcomes.restart()
            except Exception as e:
                fail = discord.Embed(description=f"```{e}```", color=self.urgecolor)
                return await ctx.send(embed=fail)

    @welcome.command(
        name='delete_after',
        aliases = ['del'],
        usage = 'Manage_channels',
        description = "Incase of raid, setup a threshold so your welcome channel won't get spammed",
        brief = "int",
        help = "```Syntax: welcome delete_after [int]\nExample: welcome delete_after 8```"
    )
    @commands.has_permissions(manage_channels=True)
    async def delete_afterr(self, ctx, threshold: int=None):
        try:
            if threshold == None:
                return await utils.send_command_help(ctx)
            elif threshold:
                check = await self.db.count_documents({ "guild_id": ctx.guild.id })
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
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "delete_after": int(threshold)}})
                    await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> **The welcome structures threshold has been set to** ``{threshold}``", color = 0x43B581))
                    self.cacheWelcomes.restart()
                else:
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "delete_after": int(threshold)}})
                    await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> **The welcome structures threshold has been set to** ``{threshold}``", color = 0x43B581))
                    self.cacheWelcomes.restart()
        except Exception as e:
            fail = discord.Embed(description=f"```{e}```", color=self.urgecolor)
            return await ctx.send(embed=fail)


    @settings.command(
        usage = 'Manage_channels',
        description = "Incase of raid, setup a threshold so your welcome channel won't get spammed",
        brief = "int",
        help = "```Syntax: welcome settings delete_after [int]\nExample: welcome settings delete_after 8```"
    )
    @commands.has_permissions(manage_channels=True)
    async def delete_after(self, ctx, threshold: int=None):
        try:
            if threshold == None:
                return await utils.send_command_help(ctx)
            elif threshold:
                check = await self.db.count_documents({ "guild_id": ctx.guild.id })
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
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "delete_after": int(threshold)}})
                    await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> **The welcome structures threshold has been set to** ``{threshold}``", color = 0x43B581))
                    self.cacheWelcomes.restart()
                else:
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "delete_after": int(threshold)}})
                    await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> **The welcome structures threshold has been set to** ``{threshold}``", color = 0x43B581))
                    self.cacheWelcomes.restart()
        except Exception as e:
            fail = discord.Embed(description=f"```{e}```", color=self.urgecolor)
            return await ctx.send(embed=fail)

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
                    params = message.replace('(embed)', '')
                    params = await utils.welcome_vars(user=member, params=params)
                    if "content:" in params.lower():
                        em = await utils.to_embed(ctx, params=message)
                        msg = await utils.to_content(ctx, params=message)
                        try:
                            return await self.bot.get_channel(chan).send(content=msg, embed=em)
                        except Exception as e:
                            return
                    else:
                        message = message.replace('(embed)', '')
                        message = await utils.welcome_vars(user=member, params=message)
                        em = await utils.to_embed(ctx, params=message)
                        try:
                            return await self.bot.get_channel(chan).send(embed=em)
                        except Exception as e:
                            return
                elif message.startswith("(embed)"):
                    message = message.replace('(embed)', '')
                    message = await utils.welcome_vars(user=member, params=message)
                    if "content:" in message.lower():
                        em = await utils.to_embed(ctx, params=message)
                        msg = await utils.to_content(ctx, params=message)
                        try:
                            return await self.bot.get_channel(chan).send(content=msg, embed=em, delete_after=dele)
                        except Exception as e:
                            return
                    else:
                        message = message.replace('(embed)', '')
                        message = await utils.welcome_vars(user=member, params=message)
                        em = await utils.to_embed(ctx, params=message)
                        try:
                            return await self.bot.get_channel(chan).send(embed=em, delete_after=dele)
                        except Exception as e:
                            return
                if not message.startswith("(embed)") and dele == None:
                    message = await utils.welcome_vars(user=member, params=message)
                    await self.bot.get_channel(chan).send(message)
                elif not message.startswith("(embed)"):
                    message = await utils.welcome_vars(user=member, params=message)
                    await self.bot.get_channel(chan).send(message, delete_after=dele)
            else:
                return
        except Exception as e:
            return




    @commands.command(name='embedsteal', extras={'perms', 'manage messages'}, aliases=['embedcode', 'getembed'], usage="```Syntax: !embedsteal <message url>\nExample: !embedsteal https://discord.com/channels/905585227269832734/905605967285211146/957383671688601691```",description='get code from an embed', brief='message_url')
    @commands.has_permissions(manage_messages=True)
    async def embedsteal(self, ctx, message_url):
        if message_url is None: return await ctx.reply(embed=discord.Embed(color=int("ff6465", 16), description=f"<:no:940723951947120650> {ctx.author.mention}: **provide a message url**"))
        parts = [x for x in message_url.replace("/"," ").split() if len(x)]
        try: channel_id,message_id = [int(x) for x in parts[-2:]]
        except: return await ctx.reply(embed=discord.Embed(color=int("ff6465", 16), description=f"<:no:940723951947120650> {ctx.author.mention}: **invalid message url**"))
        guild = ctx.guild
        if len(parts) > 2:
            if parts[-3].lower() == "@me":
                guild = self.bot
            else:
                try: guild = self.bot.get_guild(int(parts[-3]))
                except: pass
        if guild is None:
            guild = ctx.guild if ctx.guild else self.bot
        channel = guild.get_channel(channel_id)
        if not channel: return await ctx.reply(color=int("ff6465", 16), embed=discord.Embed(description=f"<:no:940723951947120650> {ctx.author.mention}: i couldn't find the channel connected to that id"))
        try: message = await channel.fetch_message(message_id)
        except: return await ctx.reply(embed=discord.Embed(color=int("ff6465", 16), description=f"<:no:940723951947120650> {ctx.author.mention}: i couldn't find the message connected to that id"))
        if not len(message.embeds): return await ctx.reply(embed=discord.Embed(color=int("ff6464", 16), description=f"<:no:940723951947120650> {ctx.author.mention}: there are not embeds attached to that message"))
        tmp = tempfile.mkdtemp()
        for index,embed in enumerate(message.embeds):
            name = "{}-{}-{}.json".format(channel_id,message_id,index)
            fp = os.path.join(tmp,name)
            m_dict = embed.to_dict()
            try:
                cc=hex(int(m_dict["color"]))
                cc=str(cc)
                cc=cc.strip('0x')
                m_dict['color']=f'#{cc}'
            except:
                pass
            try:
                m_dict['message']=f'{message.content}'
            except:
                pass
            try:
                embed=json.dumps(m_dict)
                await ctx.reply(embed=discord.Embed(description=f"<:yes:940723483204255794> {ctx.author.mention}: **successfully copied the embed code**\n\n```{embed}```", color=int("77b255", 16)))
            except Exception as e:
                pass
        shutil.rmtree(tmp,ignore_errors=True)


                
async def setup(bot):
    await bot.add_cog(welcomeRR(bot))