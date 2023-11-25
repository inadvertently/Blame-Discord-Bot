import discord, motor, Core.utils as util, asyncio
from discord.ext import commands, tasks
from colorama import Fore as f

class pojcog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db["pingonjoin"]
        self.urgecolor = 0xF3DD6C
        self.errorcol = 0xA90F25 # error color
        self.success = discord.Colour.blurple() #theme
        self.checkmoji = "<:blurple_check:921544108252741723>" # success emoji
        self.xmoji = "<:yy_yno:921559254677200957>" # unsuccessful emoji
        self.urgentmoji = "<:n_:921559211366838282>" # exclamation emoji
        self.cache = {}
        self.pings = {}
        self.clearPings.start()

    @tasks.loop(minutes=100)
    async def cachePings(self):
        cache = self.db.find({})
        guilds = []
        channels = []
        for i in await cache.to_list(length=999999):
            guild = i['guild_id']
            chan = i['channel']
            guilds.append(guild)
            channels.append(chan)
        self.cache = {guilds}

    @tasks.loop(seconds=15)
    async def clearPings(self):
        self.pings.clear()

    @clearPings.before_loop
    async def before_clearPings(self):
        await self.bot.wait_until_ready()

    @commands.group(
        aliases = ['poj', 'pingjoin'],
        usage = "Manage_channels",
        description = "Set a channel in which new members will get pinged at upon joining.",
        brief = "subcommand, arg, subarg",
        help = "```Syntax: poj [subcommand] <arg> <subarg>\nExample: poj add #rules``` "
    )
    async def pingonjoin(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Command: pingonjoin", description="Set a channel in which new memers will get pinged at upon joining.\n```Syntax: poj [subcommand] <arg> <subarg>\nExample: poj #rules 3```", color = discord.Color.blurple())
                embed.set_author(name="pingonjoin help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('pingonjoin').walk_commands()])} ・ pingonjoin")
                return await ctx.reply(embed=embed)
        except Exception as e:
            print(e)

    @pingonjoin.command(
        aliases = ['set'],
        usage = "Manage_channels",
        description = "Set a channel in which new members will get pinged at upon joining.",
        brief = "channel",
        help = "```Syntax: poj add [channel]\nExample: poj add #rules```"
    )
    #async def add(self, ctx, channel: discord.TextChannel, delete:int=None):
    @commands.has_permissions(manage_channels=True)
    async def add(self, ctx, channel: discord.TextChannel):
        try:
            get = await self.db.count_documents({ "guild_id": ctx.guild.id})
            if len(get) > 20:
                return await ctx.reply(embed=discord.Embed(description=f"{self.urgentmoji} {ctx.author.mention} This **guild** has reached it's **maximum limit** of ``20`` ping on joins.", color=self.urgecolor))
        except:
            pass
            data = await self.db.find_one({ "guild_id": ctx.guild.id, "channel": channel.id})
            print("hi")
            if data:
                return await ctx.reply(embed=discord.Embed(description=f"{self.urgentmoji} A pingonjoin already **exists** for that channel", color=self.urgecolor))
            else:
                await self.db.insert_one({
                    "guild_id": ctx.guild.id,
                    "channel": channel.id

                })
                return await ctx.reply(embed=discord.Embed(description=f"<:check:921544057312915498> **Ping on join** created for {channel.mention}", color = 0x43B581))

    
    @pingonjoin.command(
        aliases = ['del', 'remove'],
        usage = "Manage_channels",
        description = "Remove a current pingonjoin you have for a channel",
        brief = 'channel',
        help = "```Syntax: poj remove [channel]\nExample: poj remove #rules```"
    )
    @commands.has_permissions(manage_channels=True)
    async def delete(self, ctx, channel: discord.TextChannel=None):
        check = await self.db.find_one({ "guild_id": ctx.guild.id})
        if check:
            findchan = await self.db.find_one({ "guild_id": ctx.guild.id, "channel": channel.id})
            if findchan:
                await self.db.delete_one({ "guild_id": ctx.guild.id, "channel": channel.id})
                return await ctx.reply(embed=discord.Embed(description=f"<:check:921544057312915498> **pingonjoin removed** for channel {channel.mention} and will no longer be sent", color = 0x43B581))
            else:
                return await ctx.reply(embed=discord.Embed(description=f"{self.urgentmoji} **No pingonjoin exists for that channel**", color=self.urgecolor))
        else:
            return await ctx.reply(embed=discord.Embed(description=f"{self.urgentmoji} **No pingonjoin's have been created yet**, use ``poj add`` to **create one**", color=self.urgecolor))

    @pingonjoin.command(
        aliases = ['show', 'list'],
        usage = "Manage_channels",
        description = "View the current existing pinginjoin's in your server",
        brief = "None",
        help = "```Example: poj view```"
    )
    @commands.has_permissions(manage_channels=True)
    async def view(self, ctx):
        check = await self.db.find_one({ "guild_id": ctx.guild.id})
        try:
            if check:
                check_existing = self.db.find({ "guild_id": ctx.guild.id})
                channellist = []
                rows = []
                for doc in await check_existing.to_list(length = 25):
                    channels = doc['channel']
                    channellist.append(channels)
                content = discord.Embed(title="Ping On Join's", description="", color=discord.Color.blurple())
                content.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
                for count, i in enumerate(channellist, start=1):
                    rows.append(f"``{count})`` <#{i}>")
                content.set_footer(text=f"({count}/{count}) Ping On Joins", icon_url=ctx.guild.icon.url)
                await util.send_as_pages(ctx, content, rows)
            else:
                return await ctx.reply(embed=discord.Embed(description=f"{self.urgentmoji} **No pingonjoin's have been created yet**, use ``poj add`` to **create one**", color=self.urgecolor))
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            guild = member.guild
            check = await self.db.find_one({ "guild_id": guild.id})
            try:
                self.pings[member.guild.id]
            except KeyError:
                self.pings[member.guild.id] =1
            guild2 = self.pings[member.guild.id]
            self.pings[member.guild.id] = self.pings[member.guild.id]+1
            if check and not self.pings[member.guild.id] == 5:
                check_existing = self.db.find({ "guild_id": guild.id })
                for channels in await check_existing.to_list(length=25):
                    channel = guild.get_channel(channels["channel"])
                    await channel.send(member.mention, delete_after=0.8)
            else:
                return
        except:
            pass; return


async def setup(bot):
    await bot.add_cog(pojcog(bot))




        