import discord, motor, typing, asyncio, Core.utils as util, Core.confirm as cop_is_gae, Core.utils as utils
from discord.ext import commands
from typing import List
import discord.ui, re
from datetime import datetime
from Core.utils import get_theme

errorcol = 0xA90F25
urgecolor = 0xF3DD6C
success = discord.Colour.blurple()
checkmoji = "<:blurple_check:921544108252741723>"
xmoji = "<:yy_yno:921559254677200957>"
urgentmoji = "<:n_:921559211366838282>"


class autoReactioN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db['autoReaction']
        self._cd = commands.CooldownMapping.from_cooldown(1, 6.0, commands.BucketType.member)

    @commands.group(
        aliases = ['rt'],
    usage = "Manage_guild",
    description = "Set a trigger word in which the bot will respond to by reaction with the given emoji(s)",
    brief = "subcommand, argument, subarg[Optional]",
    help = "```Syntax: react [subcommand] <argument>\nExample: react jacob :star:```"
    )
    async def react(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Command: react", description="Set a trigger in which the bot will respond to by reaction with the given emoji(s)\n```Syntax: react [subcommand] <argument>\nExample: react jacob :star:```", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                embed.set_author(name="react help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('react').walk_commands()])} ・ react")
                return await ctx.send(embed=embed)
        except Exception as e:
            print(e)

    @react.command(
        name='add',
        usage = 'Manage guild',
        description = "Set a trigger word in which the bot will respond to by reaction with the given emoji(s)",
        brief = "trigger word, emoji(s)",
        help = "```Syntax: react add [trigger_word] [emojis]\nExample: react add jacob :star: :heart:```"
        )
    @commands.has_permissions(manage_guild=True)
    async def ad(self, ctx, trigger, *, emoji):
        check = await self.db.find_one({ "guild_id": ctx.guild.id, "trigger": trigger })
        now = datetime.now()
        dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
        if not check:
            if trigger.startswith("<:"):
                return await ctx.send(embed=discord.Embed(description=f"{urgentmoji} {ctx.author.mention} I need a **trigger word**", color=urgecolor))
            else:
                try:
                    emoji = re.findall('<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>', emoji)
                    a = [x[2] for x in emoji]
                    print(a)
                    if len(a) > 0:
                        good = ""
                        for i in a:
                            get = self.bot.get_emoji(int(i))
                            good += f"{get}"
                            await ctx.message.add_reaction(get)
                        print(good)
                        await self.db.insert_one({
                        "guild_id": ctx.guild.id,
                        "trigger": str(trigger),
                        "response": a,
                        "author": str(ctx.author.id),
                        "time": str(dt_string)
                        })
                        return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} The trigger {trigger} will now be reacted to with {good}", ccolor=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                    else:
                        try:
                            get = self.bot.get_emoji(a)
                            await self.db.insert_one({
                            "guild_id": ctx.guild.id,
                            "trigger": str(trigger),
                            "response": a,
                            "author": str(ctx.author.id),
                            "time": str(dt_string)
                            })
                            return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} The trigger {trigger} will now be reacted to with {good}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                        except:
                            return await ctx.send(embed=discord.Embed(description=f"{urgentmoji} {ctx.author.mention} Please make sure the emojis provided are in a mutual guild of mines.", color=urgecolor))
                except Exception as e:
                    return await ctx.send(embed=discord.Embed(description=f"{urgentmoji} {ctx.author.mention} Please make sure the emojis provided are in a mutual guild of mines.", color=urgecolor))
        else:
            return await ctx.send(embed=discord.Embed(description=f"{urgentmoji} {ctx.author.mention} This trigger word already exists in this guild", color=urgecolor))




    @react.command(
        name='remove',
        usage = 'Manage guild',
        description = "Remove a reaction trigger from your guild",
        brief = "trigger",
        help = "```Syntax: react remove [trigger_word]\nExample: react remove moist```"
        )
    @commands.has_permissions(manage_guild=True)
    async def re(self, ctx, trigger):
            check = await self.db.count_documents({ "guild_id": ctx.guild.id })
            if check:
                check_existing = await self.db.find_one({ "guild_id": ctx.guild.id, "trigger": str(trigger)  })
                if check_existing:
                    await self.db.delete_one({ "guild_id": ctx.guild.id,  "trigger": str(trigger) })
                    return await ctx.reply(embed=discord.Embed(description=f"<:check:921544057312915498> **{trigger}** has been removed and no longer will be reacted to.", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                else:
                    return await ctx.send(embed=discord.Embed(description=f"{urgentmoji} {ctx.author.mention} No results found for: **{trigger}**", color=urgecolor))
            else:
                return await ctx.reply(embed=discord.Embed(description=f"{xmoji} No reaction triggers found for this guild.", color=errorcol))



    @react.command(
        name = "list",
        aliases = ['view'],
        usage = "Manage guild",
        description = "View all the reaction triggers in your guild",
        brief = "None",
        help = "```Example: react list```"
    )
    @commands.has_permissions(manage_guild=True)
    async def ls(self, ctx):
        check = await self.db.count_documents({ "guild_id": ctx.guild.id })
        try:
            if check:
                check_existing = self.db.find({ "guild_id": ctx.guild.id})
                triggers = []
                responses = []
                authors = []
                time = []
                for doc in await check_existing.to_list(length=15):
                    trigs = doc["trigger"]
                    resps = doc["response"]
                    auths = doc["author"]
                    dates = doc["time"]
                    triggers.append(trigs)
                    responses.append(resps)
                    authors.append(auths)
                    time.append(dates)
                responseStr = [f""""**{triggers}**" \➡️ **Creator:** <@{authors}>, ``({time})``""" for triggers, authors, time in zip(triggers, authors, time)]
                rows = []
                content = discord.Embed(title=f"Reaction triggers:", description="")
                content.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
                content.color= int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)

                for count, i in enumerate(responseStr, start=1):
                    rows.append(f"``{count})`` {i}")
                content.set_footer(text=f"({count}/{count}) reaction triggers")
                await util.send_as_pages(ctx, content, rows)
            else:
                return await ctx.reply(embed=discord.Embed(description=f"{xmoji} No reaction triggers found for this guild.", color=errorcol))
        except Exception as e:
            print(e)


    @react.command(
        name='clear',
        usage = "Manage guild",
        description = "Clear all the current reaction triggers in your server.",
        brief = "None",
        help = "```Example: react clear```"
    )
    @commands.has_permissions(manage_guild=True)
    async def cl(self, ctx):
        check = await self.db.count_documents({ "guild_id": ctx.guild.id })
        if check:
            yes = await ctx.send(embed=discord.Embed(description=f"{urgentmoji} {ctx.author.mention} Are you sure you want to remove **all** of this guilds **reaction triggers**", color=urgecolor))
            msg = await ctx.send(embed=yes)
            async def confirm():
                await self.db.delete_many({ "guild_id": ctx.guild.id })
                await msg.edit(view=None, embed=discord.Embed(description=f"<:check:921544057312915498> **All** of this guilds **reaction triggers** have been removed.", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
            async def cancel():
                await msg.edit(view=None, embed=discord.Embed(description=f"{xmoji} process **cancelled**", color=errorcol))
                pass
            confirmed:bool = await cop_is_gae.confirm(self, ctx, msg)
            if confirmed:
                await confirm()
            else:
                await cancel()
        else:
            return await ctx.reply(embed=discord.Embed(description=f"{xmoji} No reaction triggers found for this guild.", color=errorcol))


    def get_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
        """Returns the ratelimit left"""
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()



    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.guild is None:
                return
            if message.author == self.bot.user:
                return
            if message.author.bot:
                return
            check = await self.db.count_documents({ "guild_id": message.guild.id })

            if check:
                check_existing = self.db.find({ "guild_id": message.guild.id })
                for trigger in await check_existing.to_list(length=50):
                    found = trigger["trigger"]
                    if found in message.content.lower():
                        ratelimit = self.get_ratelimit(message)
                        if ratelimit is None:
                            response = trigger['response']
                            for i in response:
                                try:
                                    get = self.bot.get_emoji(int(i))
                                    await message.add_reaction(get)
                                except: return
                        else:
                            return

            else:
                return
        except:
            pass; return


async def setup(bot):
    await bot.add_cog(autoReactioN(bot))