from multiprocessing import managers
import discord, asyncio, motor.motor_asyncio, humanfriendly, re, Core.confirm as cop_is_gae, aiohttp
from Core import utils as util
from discord.ext import commands, tasks
from discord.ext.commands import BucketType
from datetime import timedelta
from datetime import datetime
from datetime import date 
import Core.utils as utils, time
from Core.utils import get_theme
from colorama import Fore as f
errorcol = 0xA90F25
urgecolor = 0xF3DD6C
success = discord.Colour.blurple()
checkmoji = "<:blurple_check:921544108252741723>"
xmoji = "<:yy_yno:921559254677200957>"
urgentmoji = "<:n_:921559211366838282>"



def strip_codeblock(content):
    if content.startswith('```') and content.endswith('```'):
        return content.strip('```')
    return content.strip('` \n')

class Flags(commands.FlagConverter, prefix='--', delimiter=' ', case_insensitive=True):
    @classmethod
    async def convert(cls, ctx, argument: str):
        argument = strip_codeblock(argument).replace(' —', ' --')
        return await super().convert(ctx, argument)
    do: str = "kick" or "ban"
    accountage: int 
    threshold: int = None
    massjoin: str = None


class antiraids(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db11 = self.bot.db['antiraid']
        self.logs = self.bot.db['antiraidLogs']
        self.cache = {}
        self.cacheAntiraid.start()

    @tasks.loop(minutes=70)
    async def cacheAntiraid(self):
        getAntiraids = self.db11.find({})
        guild_ids = []
        ages = []
        antiraids = []
        ignored = []
        defaultpfps = []
        penaltys = []
        for i in await getAntiraids.to_list(length=99999):
            get_guilds = i['guild_id']
            get_ages = i['age']
            get_antiraids = i['antiraid']
            get_ignored = i['ignored']
            get_defaultpfp = i['defaultpfp']
            if not get_defaultpfp:
                get_defaultpfp = None
            get_penaltys = i['penalty']
            guild_ids.append(get_guilds)
            ages.append(get_ages)
            antiraids.append(get_antiraids)
            ignored.append(get_ignored)
            defaultpfps.append(get_defaultpfp)
            penaltys.append(get_penaltys)
        self.cache = {guild_ids:{'age': ages, 'antiraid': antiraids, 'ignored': ignored, 'penalty': penaltys, 'defaultpfp': defaultpfps} for (guild_ids, ages, antiraids, ignored, penaltys, defaultpfps) in zip(guild_ids, ages, antiraids, ignored, penaltys, defaultpfps)}
        

    @cacheAntiraid.before_loop
    async def before_cacheAntiraid(self):
        await self.bot.wait_until_ready()


    @commands.group(
        usages = 'manage_guild',
        description = 'Keep your server protected from those attempting to mass raid with new accounts or instant joins.',
        brief = 'subcommand',
        help = f'```Syntax: antiraid <subcommand>\nExample: antiraid enabled```'
    )
    async def antiraid(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Command: antiraid", description="24/7 Module to protect your server from attempted mass raids.\n```Syntax: antiraid [subcommand] <argument>\nExample: antiraid account_age 10```", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                embed.set_author(name="Antiraid help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('antiraid').walk_commands()])} ・ Antiraid")
                return await ctx.send(embed=embed)
        except Exception as e:
            print(e) 

    @antiraid.command(
        aliases = ['nopfp'],
        usage = "Manage_guild",
        description = "Allow the antiraid to take action on those who join your server with no profile picture.",
        brief = "arg",
        help = "```Syntax: antiraid defaultpfp [arg]\nExample: antiraid defaultpfp on```"
    )
    @commands.has_permissions(manage_guild=True)
    async def defaultpfp(self, ctx, arg): 
        check = await self.db11.find_one({"guild_id": ctx.guild.id })
        if check and arg == "on":
            await self.db11.update_one({"guild_id": ctx.guild.id}, {"$set": { "defaultpfp": "on"}})
            self.cacheAntiraid.restart()
            return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> The antiraid will now take action on any users who join the server with a **defaultpfp**.", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
        if check and arg == "off":
            await self.db11.update_one({"guild_id": ctx.guild.id}, {"$set": { "defaultpfp": "off"}})
            self.cacheAntiraid.restart()
            return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> The antiraid will no longer take action on those with a **defaultpfp**.", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
        if check and not arg == "on" or check and not arg == "off":
            return await ctx.send(embed=discord.Embed(description=f"{xmoji} ``arg`` must be ``on`` or ``off``", color=errorcol))
        else:
            return await ctx.send(embed=discord.Embed(description=f"{xmoji} You must set an ``antiraid account_age`` in order to proceed.", color=errorcol))
    
    @antiraid.command(
        aliases = ['punishment', 'do'],
        usage = "Manage_guild",
        description = "Set a punishment that the antiraid will use to take action on those who attempt to raid.",
        brief = 'penalty',
        help = "```Syntax: antiraid penalty [penalty]\nExample: antiraid penalty ban```"
    )
    @commands.has_permissions(manage_guild=True)
    async def penalty(self, ctx, penalty):
        check = await self.db11.find_one({"guild_id": ctx.guild.id })
        if check and penalty == "ban":
            await self.db11.update_one({"guild_id": ctx.guild.id}, {"$set": { "penalty": "ban"}})
            self.cacheAntiraid.restart()
            return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> The antiraid will now **ban** any users who don't fit the ``account_age`` requirements.", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
        if check and penalty == "kick":
            await self.db11.update_one({"guild_id": ctx.guild.id}, {"$set": { "penalty": "kick"}})
            self.cacheAntiraid.restart()
            return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> The antiraid will now **kick** any users who don't fit the ``account_age`` requirements.", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
        if check and not penalty == "kick" or check and not penalty == "ban":
            return await ctx.send(embed=discord.Embed(description=f"{xmoji} ``penalty`` must be ``kick`` or ``ban``", color=errorcol))
        else:
            return await ctx.send(embed=discord.Embed(description=f"{xmoji} You must set an ``antiraid account_age`` in order to proceed.", color=errorcol))

    @antiraid.command(
        aliases = ['logger', 'logging', 'log'],
        usage = 'Manage_guild',
        description = "Set a channel that all antiraid detections will send to",
        brief = 'channel',
        help = "```Syntax: antiraid channel [channel]\nExample: antiraid channel #logs```"
    )
    @commands.has_permissions(manage_guild=True)
    async def logs(self, ctx, channel: discord.TextChannel):
        check = await self.logs.find_one({"guild_id": ctx.guild.id })
        if check:
            return await ctx.send(embed=discord.Embed(description=f"{xmoji} An **antiraid log** channel already **exists!** ", color=errorcol))
        else:
            await self.logs.insert_one({
                "guild_id": ctx.guild.id,
                "channel": channel
            })
            return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} **Antinuke Logging** will now be sent in {channel.mention}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))

    @antiraid.command(
        aliases = ['rlog', 'clearlogs', 'removelog', 'clearlog'],
        usage = 'Manage_guild',
        description = "Remove the current antiraid channel",
        brief = 'None',
        help = "```Example: antiraid removelog```"
    )
    @commands.has_permissions(manage_guild=True)
    async def removelogs(self, ctx):
        check = await self.logs.find_one({"guild_id": ctx.guild.id })
        if not check:
            return await ctx.send(embed=discord.Embed(description=f"{xmoji} No **antiraid log** channel **exists!** ", color=errorcol))
        else:
            await self.logs.delete_one({
                "guild_id": ctx.guild.id
            })
            return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} **Antinuke Logging** will **no longer** be sent", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))) 

    @antiraid.command(
        usage = "administrator",
        description = "Ban any users that joned your server in x minutes",
        brief = 'minutes',
        help = "```Syntax: antiraid massban [minutes]\nExample: antiraid massban 10```"
    )
    @commands.has_permissions(administrator=True)
    async def massban(self, ctx, minutes):
        ids = []
        if int(minutes) > 120:
            return await ctx.send("You can only massban up to ``120`` minutes worth of accounts")
        else:
            d = discord.utils.utcnow() - timedelta(minutes=int(minutes))
            for mem in ctx.guild.members:
                sti = mem.joined_at
                if sti > d:
                    ids.append(mem.id)

            if not ids:
                return await ctx.send(f"No accounts have joined in the past ``{minutes}`` minutes")
            else:
                yes = discord.Embed(description=f"{urgentmoji} Are you sure you want to ban ``{len(ids)}`` **member(s)** who joined in the past ``{minutes}`` minutes?", color=urgecolor)
                msg = await ctx.send(embed=yes)
                yes2 = discord.Embed(description=f"<:check:921544057312915498> Initiating ban process.", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                async def confirm():
                    await msg.edit(view=None, embed=yes2)
                    count = 1
                    rows = []
                    content = discord.Embed(description = "", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                    for count, i in enumerate(ids, start=1):
                        #await ban_method(author=ctx.message.author, guildID=ctx.guild.id, userID=i)
                        await i.ban()
                        rows.append(f"``{count})`` {i}")
                    content.set_author(name=f"Banned {len(ids)} members who attempted to raid.", icon_url=ctx.guild.icon.url)
                    await util.send_as_pages(ctx, content, rows)

                async def cancel():
                    no = discord.Embed(description=f"{xmoji} Antiraid ``massban minutes`` process cancelled", color=errorcol)
                    await msg.edit(view=None, embed=no)
                    pass

                confirmed:bool = await cop_is_gae.confirm(self, ctx, msg)
                if confirmed:
                    await confirm()
                else:
                    await cancel()

 


    @antiraid.command(
        aliases = ["config", "configure", 'settings'],
        usage = "Manage_guild",
        description = "View the current antiraid settingsd within your guild",
        brief = "None",
        help = "```Example: antiraid status```"
        )
    @commands.has_permissions(manage_guild=True)
    async def status(self, ctx):
        try:
            check = await self.db11.find_one({"guild_id": ctx.guild.id}) 
            if check:
                whens = await self.db11.find_one({"guild_id": ctx.guild.id})
                when = whens['time']
                who = whens['author']
                find = whens['age']
                isenabled = whens['antiraid']
                if "Enabled" in isenabled:
                    isenabled = "<:check:921544057312915498>"
                else:
                    isenabled = "<:redTick:1007263494078484611>"
                defaultpfp = whens['defaultpfp']
                if "on" in defaultpfp:
                    defaultpfp = "<:check:921544057312915498>"
                else:
                    defaultpfp = "<:redTick:1007263494078484611>"
                penalty = whens['penalty']
                whitelisted = whens['ignored']
                meow = whens['antiraid']
                if whitelisted:
                    for i in whitelisted:
                        whitelisted = " "
                        whitelisted += f"<@{i}>"
                else:
                    whitelisted = "**None**"
                embed2 = discord.Embed(title=f"Antiraid Configuration", description=f"The antiraid is currently **{meow}** and will **{penalty}** any user accounts **not** made before **{find} day's ago**.", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)) #description=f"<:crownicon:934596375709114459> Enabled by: **{who}**\n <:pending:934596668823838730> Enabled on: **{when}**\n<:person:934597182898700319> Account age: **{find}**\n\n <:FFinfo:926308238322987058> The antiraid is currently active and is going to kick any user(s) who attempt to raid. ", color=success)
                embed2.add_field(name="Module", value=f"**Enabled**: {isenabled}\n**Enabled by:** {who}\n**Enabled On: {when}**\n**account_age:** <:check:921544057312915498>\n**defaultpfp:** {defaultpfp}\n**Penalty:** <:check:921544057312915498>\n**Whitelisted:** {whitelisted}")
                #embed2.add_field(name="Module", value=f"**account_age:** <:check:921544057312915498>\n**defaultpfp:** {defaultpfp}\n**Penalty:** <:check:921544057312915498>\n**Whitelisted:** {whitelisted}")
                embed2.set_footer(text=f"account age: {find} days")
                await ctx.send(embed=embed2)

            else:
                await ctx.send(embed=discord.Embed(description=f"{xmoji} The antiraid module hasn't been given an account_age.", color=errorcol))
        except Exception as e:
            print(e)

    @antiraid.command(
        aliases = ['age'],
        usage = 'Manage_guild',
        description = "Sets an account age in **days**. If an accounts creation date is younger than the given age then they will be kicked.",
        brief = "age",
        help = "```Syntax: antiraid account_age <account_age>\nExample: antiraid account_age 10```"
    )
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(3, 14, BucketType.user)
    async def account_age(self, ctx, age):
        async with ctx.typing():
            try:
                check = await self.db11.find_one({ "guild_id": ctx.guild.id })
                if check:
                    if age.isdigit():
                        age = int(age)
                        await self.db11.update_one({"guild_id": ctx.guild.id}, {"$set": {"age": int(age)}})
                        await asyncio.sleep(1)
                        finddit = await self.db11.find_one({"guild_id": ctx.guild.id})
                        foundit = finddit['age']
                        self.cacheAntiraid.restart()
                        return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> The antiraid **account_age** is now set to **{foundit} days**.", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                    else:
                        embed = discord.Embed(description=f"{xmoji} Argument must be an integer.", color=errorcol)
                        await ctx.send(embed=embed)
                else:
                    if age.isdigit():
                        age = int(age)
                        await self.db11.insert_one({
                            "guild_id": ctx.guild.id,
                            "age": None,
                            "time": None,
                            "author": None,
                            "antiraid": None,
                            "ignored": [],
                            "penalty": "kick",
                            "defaultpfp": None
                        })
                        await asyncio.sleep(1)
                        today = date.today()
                        d2 = today.strftime("%B %d, %Y")
                        await self.db11.update_one({"guild_id": ctx.guild.id}, {"$set": {"time": str(d2)}})
                        await self.db11.update_one({"guild_id": ctx.guild.id}, {"$set": {"author": str(ctx.author)}})
                        await self.db11.update_one({"guild_id": ctx.guild.id}, {"$set": {"antiraid": "Enabled"}})
                        await asyncio.sleep(1)
                        finddit = await self.db11.find_one({"guild_id": ctx.guild.id})
                        foundit = finddit['age']
                        self.cacheAntiraid.restart()
                        return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> The antiraid **account_age** is now set to **{foundit} days**.", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                    else:
                        embed = discord.Embed(description=f"{xmoji} Argument must be an integer.", color=errorcol)
                        await ctx.send(embed=embed)
            except Exception as e:
                print(e)

    @antiraid.command(
        aliases = ['on'],
        usage = 'Manage_guild',
        description = "Enable the antiraid in your server",
        brief = "None",
        help = "```Example: antiraid enable```"
    )
    @commands.has_permissions(manage_guild=True)
    async def enable(self, ctx):
        check = await self.db11.find_one({"guild_id": ctx.guild.id })
        if check:
            await ctx.send(embed=discord.Embed(description=f"{xmoji} **The antiraid is already enabled in this server ", color=errorcol))
        else:
            await self.db11.insert_one({
                "guild_id": ctx.guild.id,
                "age": None,
                "time": None,
                "author": None,
                "antiraid": "Enabled",
                "ignored": [],
                "penalty": "kick",
                "defaultpfp": None
            })
            self.cacheAntiraid.restart()
            return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> The **antiraid** has now been **enabled**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))

    @antiraid.command(
        aliases = ['off', 'disable'],
        usage = 'Manage_guild',
        description = "Disable the antiraid in your server",
        brief = "None",
        help = "```Example: antiraid disable```"
    )
    @commands.has_permissions(manage_guild=True)
    async def disabled(self, ctx):
        check = await self.db11.find_one({"guild_id": ctx.guild.id})
        if check:
            await self.db11.delete_one({ "guild_id": ctx.guild.id})
            self.cacheAntiraid.restart()
            return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> The **antiraid** has now been **disabled**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
        else:
            await ctx.send(embed=discord.Embed(description=f"{xmoji} **The antiraid has not been enabled in this server.** Use ``help antiraid``", color=errorcol))



    @antiraid.command(
        aliases = ['bypass', 'whitelist'],
        usage = 'Manage_guild',
        description = "Allow a user to bypass the antiraid for a certain amount of time",
        brief = "user",
        help = "```Syntax: antiraid ignore <user>\nExample: antiraid ignore blame#1457```"
    )
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(3, 14, BucketType.user)
    async def ignore(self, ctx, user: discord.User = None):
        try: 
            if user == None:
                await utils.send_command_help(ctx)
            else:
                oopp = await self.db11.find_one({"guild_id": ctx.guild.id})
                oop = oopp['antiraid']
                if "Enabled" in oop:
                    await self.db11.update_one({ "guild_id": ctx.guild.id }, { "$push": { "ignored": user.id}})
                    embed2 = discord.Embed(description=f"<:check:921544057312915498> <@{user.id}> will now be ignored from the antiraid module and can join the server without issue.", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                    self.cacheAntiraid.restart()
                    await ctx.send(embed=embed2)
                else:
                    await utils.send_command_help(ctx)
        except:
            await ctx.send(embed=discord.Embed(description=f"{xmoji} The antiraid module hasn't been given an account_age.", color=errorcol))
            pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            guild = member.guild
            try:
                oopp = self.cache[guild.id]
            except KeyError:
                return
            oop= oopp['age']
            check = oopp['antiraid']
            ignored = oopp['ignored']
            penalty = oopp['penalty']
            avatarcheck = oopp['defaultpfp']

            if "Enabled" in check:
                    if member.id in ignored:
                        return
                    else:  
                        if oop:
                            now = timedelta(days=oop).days
                            seconds = now * 24 * 60 * 60
                            if time.time() - member.created_at.timestamp() < seconds: 
                                if penalty == "kick":
                                    try:
                                        embed=discord.Embed(title=f"You've been kicked from {guild.name}!", description=f"<:icons_verified:921590533875462145> **Reason:** Detected that your account was created less than {now} days ago.\n<:icons_Person:921574656660627547> **Moderator:** blame#1457", color=int(await get_theme(self, bot=self.bot, guild=member.guild.id), 16))
                                        await member.send(embed=embed)
                                    except:
                                        pass
                                    return await member.kick(reason=f"Blame Antiraid | Account younger than {now} days.")
                                if penalty == "ban":
                                    try:
                                        embed=discord.Embed(title=f"You've been banned from {guild.name}!", description=f"<:icons_verified:921590533875462145> **Reason:** Detected that your account was created less than {now} days ago.\n<:icons_Person:921574656660627547> **Moderator:** blame#1457", color=int(await get_theme(self, bot=self.bot, guild=member.guild.id), 16))
                                        await member.send(embed=embed)
                                    except:
                                        pass
                                    return await member.ban(reason=f"Blame Antiraid | Account younger than {now} days.")
                        if avatarcheck == "on":
                            try:
                                if member.avatar is None:
                                    if penalty == "kick":
                                        try:
                                            embed=discord.Embed(title=f"You've been kicked from {guild.name}!", description=f"<:icons_verified:921590533875462145> **Reason:** Detected that your account has no profile picture.\n<:icons_Person:921574656660627547> **Moderator:** blame#1457", color=int(await get_theme(self, bot=self.bot, guild=member.guild.id), 16))
                                            await member.send(embed=embed)
                                        except:
                                            pass
                                        return await member.kick(reason=f"Blame Antiraid | Account has no profile picture")
                                    if penalty == "ban":
                                        try:
                                            embed=discord.Embed(title=f"You've been banned from {guild.name}!", description=f"<:icons_verified:921590533875462145> **Reason:** Detected that your account has no profile picture.\n<:icons_Person:921574656660627547> **Moderator:** blame#1457", color=int(await get_theme(self, bot=self.bot, guild=member.guild.id), 16))
                                            await member.send(embed=embed)
                                        except:
                                            pass
                                        return await member.ban(reason=f"Blame Antiraid | Account has no profile picture")
                            except Exception as e:
                                print(e)
                        else:
                            pass
            else:
                return


        except: pass; return


async def setup(bot):
    await bot.add_cog(antiraids(bot)) 