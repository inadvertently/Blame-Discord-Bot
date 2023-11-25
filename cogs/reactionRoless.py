import discord, random, motor.motor_asyncio, Core.utils as util
import random
from Core import utils
from discord.ext import commands

class rrroles(commands.Cog):
    def __init__(self, client):
        self.bot = client
        self.db = self.bot.db["reactionRoles"]#fetching collection 1
        self.urgecolor = 0xF3DD6C
        self.errorcol = 0xA90F25 # error color
        self.success = discord.Colour.blurple() #theme
        self.checkmoji = "<:blurple_check:921544108252741723>" # success emoji
        self.xmoji = "<:yy_yno:921559254677200957>" # unsuccessful emoji
        self.urgentmoji = "<:n_:921559211366838282>" # exclamation emoji

    @commands.group(
        aliases = ['rr', 'reactionroles'],
        usage = 'Manage_roles',
        description = "Set reaction roles for your server",
        brief = "subcommand, arg",
        help = "```Syntax: rr [subcommand] <arg>\nExample: rr add <message_id> <role> <emoji>```"

    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def reaction(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Command: Reaction Roles", description="Set reaction roles for your server\n```makefile\nSyntax: rr [subcommand] <arg>\nExample: rr add <message_id> <role> <emoji>\n```", color = discord.Color.blurple())
                embed.set_author(name="Reaction Roles help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('reaction').walk_commands()])} ・ Reaction Roles")
                return await ctx.send(embed=embed)
        except Exception as e:
            print(e) 

    @reaction.command(
        aliases = ['new'],
        usage = "Manage_roles",
        description = 'Add a new raction role to your server.',
        brief = "message_id, role, emoji",
        help = "```Syntax: rr add <message_id> <role> <emoji>\nExample: rr add 1234 5678 👍```"
        )
    @commands.has_permissions(manage_messages=True)
    async def add(self, ctx, message, role: discord.Role, emoji: discord.Emoji):
        try:
            msg = await ctx.fetch_message(message)
        except Exception:
            return await ctx.send(embed=discord.Embed(description=f"{ctx.author.mention}: {self.urgentmoji} **Invalid message ID**", color=self.urgecolor))
        if role.permissions.ban_members or role.permissions.kick_members or role.permissions.administrator or role.permissions.manage_channels or role.permissions.manage_webhooks:
            bad = discord.Embed(description=f"{self.xmoji} **roles** with **dangerous permissions** are not allowed to be reaction roles.", color= self.errorcol)
            return await ctx.send(embed=bad)
        check = await self.db.find_one({ "guild_id": ctx.guild.id, "data": message, "role": role.id, "emoji": emoji.id})
        if check:
            return await ctx.send(embed=discord.Embed(description=f"{self.urgentmoji} {ctx.author.mention}, A **reaction role** for message **{message}** and **role** <@&{role.id}>  and **emoji** {emoji} **already exist's**", color=self.urgecolor))
        else:
            
            await self.db.insert_one({
                    "guild_id": ctx.guild.id,
                    "data": message,
                    "role": role.id,
                    "emoji": emoji.id

                })
            await msg.add_reaction(str(emoji))
            return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention}, created **reaction role** for message **{message}** and **role** <@&{role.id}> and **emoji** {emoji}", color=0x43B581))

    @reaction.command(
        aliases = ['delete', 'del'],
        usage = "Manage_roles",
        description = 'Remove a current reaction role from your server',
        brief = "message_id, role",
        help = "```Syntax: rr remove <message_id> <role>\nExample: rr remove 1234 5678```"
        )
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def remove(self, ctx, message, role: discord.Role):
        try:
            msg = await ctx.fetch_message(message)
        except Exception:
            return await ctx.send(embed=discord.Embed(description=f"{ctx.author.mention}: {self.urgentmoji} **Invalid message ID**", color=self.urgecolor))
        check = await self.db.find_one({ "guild_id": ctx.guild.id})
        msgfind = check['data']
        rolefind = check['role']
        if message == msgfind and role.id == rolefind:
            await self.db.delete_one({ "guild_id": ctx.guild.id, "data": message, "role": role.id})
            return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} The reaction role was successfully deleted.", color=0x43B581))
        else:
            return await ctx.send(embed=discord.Embed(description=f"{self.urgentmoji} {ctx.author.mention}, I couldn't find anything for that **message ID** and **role** pair.", color=self.urgecolor))

    @reaction.command(
        aliases = ['view'],
        name = "list",
        usage = "Manage_roles",
        description = "View all reaction roles in the guild",
        brief = "None",
        help = "```Example: rr list```"
    )
    @commands.has_permissions(manage_guild=True)
    async def ls(self, ctx):
        check = await self.db.count_documents({ "guild_id": ctx.guild.id })
        try:
            if check:
                check_existing = self.db.find({ "guild_id": ctx.guild.id})
                messages = []
                emojis = []
                roles = []
                #time = []
                for doc in await check_existing.to_list(length=100):
                    m = doc["data"]
                    e = doc["emoji"]
                    r = doc["role"]
                    #dates = doc["time"]
                    messages.append(m)
                    emojis.append(e)
                    roles.append(r)
                    #time.append(dates)
                responseStr = [f""""**Message ID:** ``{messages}`` | **Reaction:** {self.bot.get_emoji(emojis)} | **Role:** <@&{roles}>""" for messages, emojis, roles in zip(messages, emojis, roles)]
                rows = []
                content = discord.Embed(title=f"Reaction roles:", description="")
                content.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
                content.color= discord.Color.blurple()

                for count, i in enumerate(responseStr, start=1):
                    rows.append(f"``{count})`` {i}")
                content.set_footer(text=f"({count}/{count}) Reaction Roles")
                await util.send_as_pages(ctx, content, rows)
            else:
                return await ctx.send("No reaction roles in this guild") 
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        try:
            data = await self.db.find_one({"guild_id": payload.member.guild.id, "data": str(payload.message_id), "emoji": payload.emoji.id})
            if data:
                print('yes')
                guild = self.bot.get_guild(payload.member.guild.id)
                role = guild.get_role(data["role"])
                await payload.member.add_roles(role, reason="Blame reactions roles")
            else:
                return
        except: pass; return
        
async def setup(bot):
    await bot.add_cog(rrroles(bot))