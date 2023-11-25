import discord, motor.motor_asyncio
from discord.ext import commands
import db.database 
from Core.utils import get_theme
db.database.prefixes = {}
db.database.default_prefix = ';'

class prefixSet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db1 = self.bot.db['prefix']

    @commands.hybrid_group(
        aliases = ['setprefix', 'prefixset', 'changeprefix'],
        usage = 'Manage guild',
        description = "Changes the bots prefix in the current server",
        brief = " new_prefix",
        help = "```Syntax: setprefix [new_prefix]\nExample: setprefix !!```"
    )
    async def prefix(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Command: prefix", description="View, change or remove you servers current prefix\n```Syntax: prefix [subcommand] <argument>\nExample: prefix set ,```", color = discord.Color.blurple())
                embed.set_author(name="prefix help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('prefix').walk_commands()])} ・ prefix")
                return await ctx.send(embed=embed)
        except Exception as e:
            print(e)

    @prefix.command(
        aliases = ['change', 'add'],
        usage = 'Manage-guild',
        description = "change the guilds current prefix",
        brief = 'new_prefix',
        help = "```Syntax: prefix set [new_prefix]\nExample: prefix set ;```"
    )
    @commands.has_permissions(manage_guild=True)
    async def set(self, ctx, new_prefix):
        if len(new_prefix) > 5:
            return await ctx.send(embed=discord.Embed(description = f"<:yy_yno:921559254677200957> The ``new_prefix`` **cannot** be longer than **5 characters.**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
        else:
            await self.db1.update_one({ "guild_id": ctx.guild.id }, { "$set": { "prefix": str(new_prefix)}})
            data = await self.db1.find_one({ "guild_id": ctx.guild.id })

            pref = data['prefix']
            db.database.prefixes[ctx.guild.id]=pref #cache it
            print(db.database.prefixes)

            return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} **You've set** the **guilds prefix** to ``{new_prefix}``", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))

    @prefix.command(
        aliases = ['delete'],
        usage = 'Manage_guild',
        description ="Delete the guilds current prefix",
        brief = "None",
        help = "```Example: prefix delete```"
    )
    @commands.has_permissions(manage_guild=True)
    async def remove(self, ctx):
        try:
            await self.db1.delete_one({
                "guild_id": ctx.guild.id
            })
            db.database.prefixes[ctx.guild.id] = db.database.default_prefix
            return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} You've **removed** the **guilds prefix.** It is now **set to** ``{default_prefix}`` by **default.**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
        except: pass; return
            
            
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
            await self.db1.insert_one({
                "guild_id": guild.id,
                "prefix": f";"
            })
            try:
                db.database.prefixes.pop(guild.id, None)
            except: pass; return

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            await self.db1.delete_one({
                "guild_id": guild.id
            })
            db.database.prefixes[guild.id] = db.database.default_prefix
        except: pass; return



async def setup(bot):
    await bot.add_cog(prefixSet(bot))