import discord, motor, traceback, importlib, string, secrets, aiohttp, typing, difflib
from discord.ext import commands
from Core.utils import count
from discord.ext.commands import errors
from Core import exceptions, log
import asyncio,random,logging, traceback
from fuzzywuzzy import fuzz as fuzzywuzzy
from discord.app_commands import AppCommandError
from Core import utils as util
from Core import utils, log
import button_paginator as pg
from Core.utils import get_theme

logger=logging.getLogger(__name__)
command_logger=logging.getLogger(__name__)

errorcol = 0xA90F25
xmoji = "<:yy_yno:921559254677200957>"
developers = [714703136270581841, 236522835089031170, 386192601268748289, 753277825372389402]

class RenameInput(discord.ui.Modal, title='Search for a command'):
    def __init__(self, ctx, bot):
        super().__init__()
        self.bot=bot
        self.ctx = ctx

    renamee = discord.ui.TextInput(label='Command', placeholder="Enter the closest match:")

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            ctx=self.ctx
            cmd = self.renamee.value.lower()
            restricted = ['newservers', 'topservers', 'serverinv', 'mutual_servers']
            cmds = [command.name.lower() for command in self.bot.walk_commands() if cmd in command.name.lower() and not command.name in restricted]
            closest = difflib.get_close_matches(self.renamee.value.lower(), cmds,n=10, cutoff=0)
            found = []
            if closest:
                for i in closest:
                    found.append(i)
            if len(found):
                embeds = []
                for i in found:
                    print(i)
                    get = self.bot.get_command(i)
                    embed = discord.Embed(title=f"Command: {get.name}", description=get.description, color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                    if get.aliases:
                        embed.add_field(name="Aliases", value=", ".join(get.aliases), inline=False)
                    else:
                        embed.add_field(name="Aliases", value="None")
                    embed.add_field(name="⚠️ Parameters", value=get.brief)
                    embed.add_field(name="🔒 Permissions", value=get.usage)
                    embeds.append(embed)
                    if get.help:
                        usage=get.help
                        embed.add_field(name="📲 Usage", value=f"{usage}", inline=False)
                    embed.set_footer(text=f"Module: {get.cog_name}.py ・ Entry: ({len(embeds)}/{len(found)} entries)")
                paginator = pg.Paginator(self.bot, embeds, ctx, invoker=interaction.user.id)
                if len(embeds) > 1:
                    paginator.add_button('prev', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.blurple)
                    paginator.add_button('first', emoji='<:Settings:921574525815103528>', style=discord.ButtonStyle.green)
                    paginator.add_button('next', emoji='<:right:934237462660788304>', style=discord.ButtonStyle.blurple)
                    paginator.add_button('goto', emoji='🔢', style=discord.ButtonStyle.grey)
                    #paginator.add_button('goto', label="📋 Commands found.", disabled=True, style=discord.ButtonStyle.grey)
                await interaction.response.defer()
                return await paginator.start()
            else:
                await interaction.response.defer()
                return await utils.send_issue(ctx, "No similar commands found..")

        except:
            pass
            await interaction.response.defer()
            return await utils.send_issue(ctx, "No similar commands found..")


class aaa(discord.ui.View):
    def __init__(self, ctx, bot):
        super().__init__(timeout=None)
        self.value = 0
        self.bot = bot
        self.ctx = ctx
        
    @discord.ui.button(label="🔍 Find or lookup commands!", style=discord.ButtonStyle.green)
    async def name(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx=self.ctx
        await interaction.response.send_modal(RenameInput(ctx, self.bot))
        button.disabled = True
        button.label = "📋 Commands found."
        await asyncio.sleep(5)
        await interaction.message.edit(embed=None, view=self)
        
class commandHandle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.errors={}
        self._cd = commands.CooldownMapping.from_cooldown(1, 6.0, commands.BucketType.member)
        self.db = self.bot.db["globalCommands"] #fetching collection 1
        self.db2 = self.bot.db["userCommands"]
        self.db3 = self.bot.db['cmdStats']
        self.status = self.bot.db['commandStatus']
        self.fakeperms = self.bot.db['fakeperms']
        self.msgss = self.bot.db["messageCount"]
        self.errorLog = self.bot.get_channel(1040441902094364724)

        self.message_levels = {
            "info": {
                "description_prefix": ":information_source:",
                "color": int("3b88c3", 16),
                "help_footer": False,
            },
            "warning": {
                "description_prefix": ":warning:",
                "color": int("ffcc4d", 16),
                "help_footer": False,
            },
            "error": {
                "description_prefix": ":no_entry:",
                "color": int("be1931", 16),
                "help_footer": False,
            },
            "cooldown": {
                "description_prefix": ":hourglass_flowing_sand:",
                "color": int("ffe8b6", 16),
                "help_footer": False,
            },

        }


    def get_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
        """Returns the ratelimit left"""
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()

    async def send(self, ctx, level, message, help_footer=None, codeblock=False, **kwargs):
        """Send error message to chat."""
        refcode=''.join((secrets.choice(string.ascii_letters) for i in range(5)))
        if not refcode in self.errors:
            pass
        try:
            self.errors[refcode]=[]
            self.errors[refcode].append(f"**Guild:** `{ctx.guild.id}`\n**Trigger:** `{ctx.message.clean_content}`\n**Error:** ```{message}```")
        except:
            pass
        settings = self.message_levels.get(level)
        if codeblock:
            message = f"`{message}`"

        embed = discord.Embed(
            color=settings["color"], description=f"{settings['description_prefix']} {message} \n**Error Code:** `{refcode}`"
        )

        embed2 = discord.Embed(
            color=settings["color"], title="Developer Message",  description=f"Uh-oh, an error was caught. {settings['description_prefix']} {message} \n**Error Code:** `{refcode}`"
        )

        help_footer = help_footer or settings["help_footer"]
        if help_footer:
            embed.set_footer(text=f"Learn more: {ctx.prefix}help {ctx.command.qualified_name}")
            embed2.set_footer(text=f"Something went wrong!")

        try:
            await ctx.send(embed=embed, **kwargs)
            await self.errorLog.send(embed=embed2, **kwargs)
        except discord.errors.Forbidden:
            self.bot.logger.warning("Forbidden when trying to send error message embed")

    async def send2(self, ctx, level, message, help_footer=None, codeblock=False, **kwargs):
        """Send error message to chat."""
        refcode=''.join((secrets.choice(string.ascii_letters) for i in range(5)))
        if not refcode in self.errors:
            pass
        try:
            self.errors[refcode]=[]
            self.errors[refcode].append(f"**Guild:** `{ctx.guild.id}`\n**Trigger:** `{ctx.message.clean_content}`\n**Error:** ```{message}```")
        except:
            pass
        settings = self.message_levels.get(level)
        if codeblock:
            message = f"`{message}`"

        embed = discord.Embed(
            color=settings["color"], title="Developer Message", description=f"Uh-oh, an error was caught. {settings['description_prefix']} {message} \n**Error Code:** `{refcode}`"
        )

        help_footer = help_footer or settings["help_footer"]
        if help_footer:
            embed.set_footer(text=f"Something went wrong!")

        try:
            await self.errorLog.send(embed=embed, **kwargs)
        except discord.errors.Forbidden:
            self.bot.logger.warning("Forbidden when trying to send error message embed")

    async def log_and_traceback(self, ctx, error):
        logger.error(f'Unhandled exception in command "{ctx.message.content}":')
        exc = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        logger.error(exc)
        await self.send2(ctx, "error", f"{type(error).__name__}: {error}", codeblock=True)

    @commands.command(
        aliases = ['lookup', 'find', 'cmd'],
        description = "Forgot the name of a command? Let's find it!",
        usage = 'send_messages',
        brief = 'command',
        help = "```Example: lookup```"
    )
    async def search(self, ctx):
        embed = discord.Embed(description=f"**Forgot the name of a command? Let's find it!**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
        await ctx.send(embed=embed, view=aaa(ctx=ctx, bot=self.bot))

    @commands.command(
        aliases = ['dcmd', 'disable'],
        description = "Disable a command in your server",
        usage = 'administrator',
        brief = 'command',
        help = '```Syntax: disable [command_name]\nExample: disable ping```'
    )
    @commands.has_permissions(administrator=True)
    async def disablecommand(self, ctx, commands):
        find = await self.status.find_one({'guild_id': ctx.guild.id})
        restricted = ['newservers', 'topservers', 'serverinv', 'mutual_servers']
        cmds = [command.name.lower() for command in self.bot.walk_commands() if not command.name in restricted]
        if commands in cmds:
            if not find:
                await self.status.insert_one({
                    'guild_id': ctx.guild.id,
                    'disabled': [f"{commands}"]
                })
                return await util.send_blurple(ctx, f"The command: ``{commands}`` is now disabled in this server.")
            else:
                await self.status.update_one({ "guild_id": ctx.guild.id }, { "$push": { "disabled": commands}}) 
                return await util.send_blurple(ctx, f"The command: ``{commands}`` is now disabled in this server.")
        else:
            return await util.send_issue(ctx, f"Command: ``{commands}`` does not exist.")

    @commands.command(
        aliases = ['enable', 'ecmd'],
        description = "Enable a disabled command in your server",
        usage = 'administrator',
        brief = 'command',
        help = '```Syntax: enable [command_name]\nExample: enable ping```'
    )
    @commands.has_permissions(administrator=True)
    async def enablecommand(self, ctx, commands):
        find = await self.status.find_one({'guild_id': ctx.guild.id})
        restricted = ['newservers', 'topservers', 'serverinv', 'mutual_servers']
        cmds = [command.name.lower() for command in self.bot.walk_commands() if not command.name in restricted]
        if commands in cmds:
            if find:
                if commands in find['disabled']:
                    await self.status.update_one({ "guild_id": ctx.guild.id }, { "$pull": { "disabled": commands }})
                    return await util.send_blurple(ctx, f"The command: ``{commands}`` is now enabled in this server.")
                else:
                    return await util.send_issue(ctx, f"Command: ``{commands}`` is not disabled in this server.")
            else:
                return await util.send_issue(ctx, f"Command: ``{commands}`` is not disabled in this server.")
        else:
            return await util.send_issue(ctx, f"Command: ``{commands}`` does not exist.")

    


    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        cmdfind = await self.db3.find_one({"command": str(ctx.command)})
        if not cmdfind:
            await self.db3.insert_one({
                "command": str(ctx.command),
                "uses": 1
            })
        else:
            cnt = cmdfind['uses']
            cmd_add = cnt + 1
            await self.db3.update_one({"command": str(ctx.command)}, { "$set": { "uses": cmd_add}})
        oop = await self.db.find_one({"start": "June 8th, 2022"})
        counter = oop["count"]
        normal_count = int(counter)
        adding = normal_count + 1
        await self.db.update_one({ "start": "June 8th, 2022" }, { "$set": { "count": adding}})
        command = ctx.command
        command_logger.info(await log.log_command(ctx))

        try:
            findauthor = await self.db2.find_one({"author": ctx.author.id})
            if findauthor:
                authorcount = findauthor["count"]
                foundcount = int(authorcount)
                addcount = foundcount + 1
                await self.db2.update_one({ "author": ctx.author.id }, { "$set": { "count": addcount}})
                roles = {50: 1040982042638299146, 100: 1040982123659669596, 250: 1040982158237520033, 500: 1040982148963897346, 850: 1040982273731858462, 1000: 1040982276403630100, 1500: 1040982354329604177, 2000: 1040982351896916008, 2500: 1040995789234786364, 2700: 1040995789234786364, 3000: 1040995678656143421, 3100: 1040995678656143421, 3500: 1040982399225430077, 5000: 1040982452312735794}
                guild =self.bot.get_guild(818179462918176769)
                names = [guild.get_role(roles[i]).name for i in roles if addcount == i]
                if names:
                    return await ctx.reply(embed=discord.Embed(title="Congrats :tada:", description = f"You have ran over **{names[-1]}+ commands**. You can claim **role perks** in the **[support server](https://discord.gg/blame) using the ``claim`` command.!**", color=discord.Color.blurple()).set_thumbnail(url="https://creazilla-store.fra1.digitaloceanspaces.com/emojis/55254/party-popper-emoji-clipart-xl.png"))
                else:
                    return

            else:
               await self.db2.insert_one({
           "author": ctx.author.id,
            "count": 1
                })
        except Exception as e:
            print(e)

    @commands.command(aliases = ["globalcmds", 'allcmds', 'allcommands', 'globalcommands', 'global', 'cmds', 'simplelookup', 'simplesearch'])
    async def globalc(self, ctx, user: discord.User=None):
        async with ctx.typing():
            if ctx.author.id in developers:
                if user:
                    finduser = await self.db2.find_one({"author": user.id})
                    if finduser:
                        authorcount = finduser["count"]
                        a = "{:,}".format(authorcount)
                        img = user.display_avatar.url
                        try:
                            color=int(await utils.color_from_image_url(url=img), 16)
                            embed = discord.Embed(title = "Results Found...", description=f"<a:clyde:921754257835827200> **User:** {user}\n<:edit:921595840647282729> **ID:** {user.id}\n<:join:921595822624370708> **Created:** {discord.utils.format_dt(user.created_at, style='f')} **({discord.utils.format_dt(user.created_at, style='R')})** ", color=color)
                            embed.set_thumbnail(url = user.display_avatar.url)
                            embed.set_footer(text=f"⚙️ Commands ran: {a}", icon_url=user.display_avatar.url)
                            await ctx.send(embed=embed)
                        except:
                            embed = discord.Embed(title = "Results Found...", description=f"<a:clyde:921754257835827200> **User:** {user}\n<:edit:921595840647282729> **ID:** {user.id}\n<:join:921595822624370708> **Created:** {discord.utils.format_dt(user.created_at, style='f')} **({discord.utils.format_dt(user.created_at, style='R')})** ", color=0x77858e)
                            embed.set_thumbnail(url = user.display_avatar.url)
                            embed.set_footer(text=f"⚙️ Commands ran: {a}", icon_url=user.display_avatar.url)
                            await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(description=f"```{user} has not ran any commands.```")
                        return await ctx.send(embed=embed)
                else:
                    oop = await self.db.find_one({"start": "June 8th, 2022"})
                    counter = oop["count"]
                    a = "{:,}".format(counter)
                    return await ctx.send(f"<a:globe:921613254168547388> {a} commands ran.")
            else:
                return await ctx.send("You're not a developer.")


    @commands.Cog.listener()
    async def on_message(self, message):
        try:
        #ratelimit = self.get_ratelimit(message)
        #if ratelimit is None:
            #find = await self.msgss.find_one({"guild_id": message.guild.id, "user": message.author.id})
         ##   if find and not message.author.id == self.bot.user.id and not message.author.bot:
                #newCount = find["count"]+1
               # await self.msgss.update_one({"guild_id": message.guild.id, "user": message.author.id}, {"$set": {"count": newCount}})
           # else:A
               # if message.author.id == self.bot.user.id:
                  #  return
                #else:
                  # await self.msgss.insert_one({
                      #  "guild_id": message.guild.id,
                       # "user": message.author.id,
                       # "count": 1})
        #else:
          #  return
        #try:
            if message.guild.id == 818179462918176769 and message.channel.id == 1006646551331999875:
                if message.author.id == 236522835089031170 and message.content.lower().startswith("how to"):
                    return await message.channel.send("Start off your message with **+vouch** to leave your vouch :thumbsup:")
                if message.content.lower().startswith("+vouch"):
                    await message.add_reaction("<:W_:1005275850024960091>")
                    return
                else:
                    if not message.author.id == 776128410547126322:
                        return await message.delete()
            if message.guild.id == 818179462918176769 and message.channel.id == 1027772796744519770:
                return await message.delete()
            else:
                return
        except:
            pass; return


   # @commands.command(
    #    aliases = ['lb', 'actives', 'top'],
    #    usage = "send_messages",
   #     description = 'Check the guilds current message leaderboard',
    #    brief = "None",
    #    help = "```Example: leaderboard```"
   # )
    #async def leaderboard(self, ctx):
       # async with ctx.typing():
          #  try:
            #    find = self.msgss.find({ "guild_id": ctx.guild.id}).sort("count", -1)
              #  found = []
               # userfind = []
               # for user in await find.to_list(length=10):
                  #  founds = user['count']
                   # users = user['user']
                   # found.append(founds)
                   # userfind.append(users)
                #resp = [f"""<@{userfind}> - **{found} msgs**""" for userfind, found in zip(userfind, found)]
               # rows = []
                #embed = discord.Embed(title="Most active members :speaking_head:", color=discord.Color.blurple())
               # embed.description = ""
               # embed.set_footer(text="Top 10 actives")

               # for count, i in enumerate(resp, start=1):
                  #  rows.append(f"**{count}.** {i}")
                #await util.send_as_pages(ctx, embed, rows)
           # except Exception as e:
               # print(e)

    @commands.command(aliases = ['clb'])
    async def cleaderboard(self, ctx):
        async with ctx.typing():
            find = self.db2.find({}).sort("count", -1)
            found = []
            userfind = []
            for user in await find.to_list(length=100):
                found.append(user['count'])
                userfind.append(self.bot.get_user(user['author']))
            resp = [f"""[{userfind}](https://blame.gg) - **{found} commands**""" for userfind, found in zip(userfind, found)]
            rows = []
            embed = discord.Embed(title="Top users", color=discord.Color.blurple())
            embed.description = ""
            for count, i in enumerate(resp, start=1):
                #embed.set_footer(text=f"Pages: {len(rows)}/{len(resp)}")
                rows.append(f"**{count}.** {i}")
            await util.send_as_pages(ctx, embed, rows)


    @commands.command(aliases = ['tc', 'topcmds'])
    async def topcommands(self, ctx):
        async with ctx.typing():
            try:
                find = self.db3.find({}).sort("uses", -1)
                found = []
                userfind = []
                for user in await find.to_list(length=100):
                    founds = user['uses']
                    users = user['command']
                    found.append(founds)
                    userfind.append(users)
                    
                resp = [f"""{userfind} - **{found} commands**""" for userfind, found in zip(userfind, found)]
                rows = []
                embed = discord.Embed(title="Top Commands", color=discord.Color.blurple())
                embed.description = ""
                for count, i in enumerate(resp, start=1):
                    rows.append(f"**{count}.** {i}")
                await util.send_as_pages(ctx, embed, rows)
            except Exception as e:
                print(e)

    @commands.command(
        aliases = ['messages', 'msg', 'activity'],
        usage = "send_messages",
        description = "Check how many messages you or another member have in the server",
        brief = "member[Optional]",
        help = "```Syntax: messages [member]\nExample: messages @jacob```"
    )
    async def msgs(self, ctx, member:discord.Member=None):
        if member == None:
            member = ctx.author
        find = await self.msgss.find_one({ "guild_id": ctx.guild.id, "user": member.id})
        if find:
            amount = find['count']
            return await util.send_blurple(ctx, f"{member.mention}** has **{amount} messages.")
        else:
            return await util.send_error(ctx, f"{member.mention}** has **0 messages.")



    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command."""
        # ignore if command has it's own error handler
        if hasattr(ctx.command, "on_error"):
            return

        # extract the original error from the CommandError wrapper
        error = getattr(error, "original", error)


        # silently ignored expections
        if isinstance(error, (commands.CommandNotFound)):
            return
            er=str(error).split(" ")
            invalid_command=er[1]
            acommand_list = [command.qualified_name.lower() for command in self.bot.commands]
            command_list=[]
            for command in self.bot.commands:
                command_list.append(command.aliases)
            fuzzy_ratios = []
            for command in command_list:
               ratio = fuzzywuzzy.ratio(invalid_command, command)
               fuzzy_ratios.append(ratio)

            max_ratio_index = fuzzy_ratios.index(max(fuzzy_ratios))
            fuzzy_matched = command_list[max_ratio_index]

            return await ctx.invoke(self.bot.get_command(fuzzy_matched[0]))

        if isinstance(error, commands.DisabledCommand):
            command_logger.warning(log.log_command(ctx, extra=error))
            return await self.send(
                ctx,
                "info",
                "This command is temporarily disabled, sorry for the inconvenience!",
            )

        if isinstance(error, commands.MissingRequiredArgument):
            #return await util.send_command_help(ctx)
            return await ctx.send_help(ctx.invoked_subcommand or ctx.command)
        if isinstance(error, commands.BadUnionArgument):
            if len(error.converters) > 1:
                converters = ', '.join(map(
                    lambda c: f'`{c.__name__}`', error.converters[:-1])) + f' and `{error.converters[-1].__name__}`'
            else:
                converters = f'`{error.converters[0].__name__}`'
            #message = f'Converting to {converters} failed for parameter `{error.param.name}`'
            #await ctx.send(message)
            return await ctx.reply(embed=discord.Embed(color=int("faa61a", 16), description=f"{ctx.author.mention}: **{error.param.name} not found**"))

        if isinstance(error, exceptions.Info):
            command_logger.info(log.log_command(ctx, extra=error))
            return await self.send(ctx, "info", f"{str(error)}", error.kwargs)
        if isinstance(error, exceptions.Warning):
            command_logger.warning(log.log_command(ctx, extra=error))
            return await self.send(ctx, "warning", f"{str(error)}", error.kwargs)
        command_logger.error(
            f'{type(error).__name__:25} > {ctx.guild} : {ctx.author} "{ctx.message.content}" > {error}'
        )

        if isinstance(error, exceptions.Error):
            await self.send2(ctx, "error", str(error), error.kwargs)
            return await self.send(ctx, "error", str(error), error.kwargs)

        if isinstance(error, commands.NoPrivateMessage):
            try:
                await self.send(
                    ctx.author,
                    "info",
                    "This command cannot be used in DM",
                )
            except (discord.HTTPException, discord.errors.Forbidden):
                pass

        elif isinstance(error, commands.MissingPermissions):
            permissions = "\n".join([i.upper() for i in error.missing_permissions])
            permissions=permissions.lower()
            roles = [role.id for role in ctx.author.roles]
            check = await self.fakeperms.find_one({"guild_id": ctx.guild.id, 'object': ctx.author.id})
            check2 = await self.fakeperms.find_one({"guild_id": ctx.guild.id, 'object': { "$in": roles}})
            if check2:
                if permissions in check2['fakeperms']:
                    return await ctx.reinvoke()
                else:
                    embed = discord.Embed(description=f"{ctx.author.mention}: You're ***missing*** permission `{permissions}`", color=int("faa61a", 16))
                    return await ctx.send(embed=embed)
            elif check:
                if permissions in check['fakeperms']:
                    return await ctx.reinvoke()
                else:
                    embed = discord.Embed(description=f"{ctx.author.mention}: You're ***missing*** permission `{permissions}`", color=int("faa61a", 16))
                    return await ctx.send(embed=embed)
            else:
                embed = discord.Embed(description=f"{ctx.author.mention}: You're ***missing*** permission `{permissions}`", color=int("faa61a", 16))
                return await ctx.send(embed=embed)

        elif isinstance(error, commands.BotMissingPermissions):
            perms = ", ".join(f"**{x}**" for x in error.missing_perms)
            await self.send(
                ctx, "warning", f"Cannot execute command! Bot is missing permission {perms}"
            )

        elif isinstance(error, commands.errors.MaxConcurrencyReached):
            await ctx.send("Another game is currently in activity")

        elif isinstance(error, commands.NoPrivateMessage):
            await self.send(ctx, "info", "You cannot use this command in private messages!")

        elif isinstance(error, (commands.NotOwner, commands.CheckFailure)):
            pass
            #await self.send(ctx, "error", "You cannot use this command.")

        elif isinstance(error, (commands.BadArgument)):
            await self.send(ctx, "warning", str(error), help_footer=True)

        elif isinstance(error, discord.errors.Forbidden):
            try:
                await self.send(ctx, "error", str(error), codeblock=True)
            except discord.errors.Forbidden:
                try:
                    await ctx.message.add_reaction("🙊")
                except discord.errors.Forbidden:
                    await self.log_and_traceback(ctx, error)

        elif isinstance(error, commands.CommandOnCooldown):
            if ctx.author in self.bot.owner_ids:
                try:
                    await ctx.reinvoke()
                    return
                except Exception as e:
                    await self.on_command_error(ctx, e)
            else:
                await self.send(
                    ctx,
                    "cooldown",
                    f"You are on cooldown. Please wait `{error.retry_after:.0f} seconds`",
                delete_after=5)

        else:
            await self.log_and_traceback(ctx, error)

    @commands.command(name="error", aliases=['trace', 'traceback'], hidden=True)
    @commands.is_owner()
    async def error(self, ctx, reference):
        if reference in self.errors:
            return await ctx.send(embed=discord.Embed(color=discord.Colour.gold(), description=f"{self.errors[reference][0]}"))
        else:
            return await util.send_bad(ctx, f"no error found under reference code `{reference}`")

    @commands.command(name='reloadutils', aliases=['rl'])
    @commands.is_owner()
    async def reloadutils(self, ctx, name: str):
        """ Reloads a utils module. """
        name_maker = f"Core/{name}.py"
        module_name = importlib.import_module(f"Core.{name}")
        importlib.reload(module_name)
        await ctx.send(f"Reloaded module **{name_maker}**")

async def setup(bot):
    await bot.add_cog(commandHandle(bot))
