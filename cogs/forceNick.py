import discord, motor.motor_asyncio, Core.utils as util
from discord.ext import commands

class forceNickBud(commands.Cog):
    def __init__(self, client):
        self.bot = client  
        self.db = self.bot.db['forceNick']
        self.errorcol = 0xA90F25 # error color
        self.urgecolor = 0xF3DD6C # exclamation color
        self.success = discord.Colour.blurple() #theme
        self.checkmoji = "<:blurple_check:921544108252741723>" # success emoji
        self.xmoji = "<:yy_yno:921559254677200957>" # unsuccessful emoji
        self.urgentmoji = "<:n_:921559211366838282>" # exclamation emoji

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        try:
            check = await self.db.find_one({"guild_id": before.guild.id, "user_id": before.id})
            if check:
                if before.nick != after.nick:
                    findforce = check['nickname']
                    await after.edit(nick=findforce)
                else:
                    return
            else:
                return
        except: pass; return

    @commands.group(
        aliases = ['fn', 'force', 'fnick'],
        usage = "Mange_nicknames",
        description = "Force a nickname on someone so if they change it, it'll get reverted to whatever it's forced to",
        brief = "member, nickname",
        help = "```Syntax: forcenick add [member] <nickname>\nExample: forcenick add @jac#1337 leet``` "
    )
    async def forcenick(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Command: forcenick add", description="Force a nickname on someone so if they change it, it'll get reverted to whatever it's forced to\n```Syntax: forcenick add [member] <nickname>\nExample: forcenick add @jac#1337 leet```", color = discord.Color.blurple())
                embed.set_author(name="Forcenick help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('forcenick').walk_commands()])} ・ Forcenick")
                return await ctx.send(embed=embed)
        except Exception as e:
            print(e)
    


    @forcenick.command(
        aliases = ['ls', 'all', 'view'],
        usage = "Manage_nicknames",
        description= "View all forcenick names in the server",
        brief = 'None',
        help = "```Example: forcenick list```"
    )
    @commands.has_permissions(manage_nicknames=True)
    async def list(self, ctx):
        async with ctx.typing():
            check = self.db.find({ "guild_id": ctx.guild.id})
            if check:
                members = []
                forcenicks = []
                for doc in await check.to_list(length=50):
                    memb = doc['user_id']
                    nicknam = doc['nickname']
                    members.append(memb)
                    forcenicks.append(nicknam)
                responseStr = [f""""**{forcenicks}**" :arrow_right: Member: <@{members}>, ``({members})``""" for members, forcenicks in zip(members, forcenicks)]
                rows = []
                content = discord.Embed(title=f"Forcenickname's in {ctx.guild.name}", description="", color = discord.Color.blurple())
                content.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

                for count, i in enumerate(responseStr, start=1):
                    rows.append(f"``{count})`` {i}")
                content.set_footer(text=f"({count}/{len(i)}) forcenicks • (forcenick [member] None) to remove a forcenick.")
                await util.send_as_pages(ctx, content, rows)
            else:
                return await ctx.send("No forcenicks in this guild") 

    @forcenick.command(
        aliases = ['fn', 'force', 'fnick'],
        usage = "Mange_nicknames",
        description = "Force a nickname on someone so if they change it, it'll get reverted to whatever it's forced to",
        brief = "member, nickname",
        help = "```Syntax: forcenick add [member] <nickname>\nExample: forcenick add @jac#1337 leet``` "
    )
    @commands.has_permissions(manage_nicknames=True)
    async def add(self, ctx, member: discord.Member, *, nickname):
        check = await self.db.find_one({ "guild_id": ctx.guild.id, "user_id": member.id})
        if check:
            embed = discord.Embed(description=f"{self.urgentmoji} {ctx.author.mention}: {member.mention} already has an **existing forcenick** in this server.", color=self.urgecolor)
            return await ctx.send(embed=embed) 
        if len(nickname) > 26:
            embed = discord.Embed(description=f"{self.urgentmoji} A username cannot be longer than 25 characters", color=self.urgecolor)
            return await ctx.send(embed=embed)
        if nickname == "None":
            await self.db.delete_one({ "guild_id": ctx.guild.id, "user_id": member.id})
            await member.edit(nick=None)
            embed3 = discord.Embed(description = f"<:check:921544057312915498> Forcenick for <@{member.id}> has been **removed**", color=0x43B581)
            return await ctx.send(embed=embed3)
        if ctx.author.top_role.position <= member.top_role.position and ctx.author != ctx.guild.owner:
            return await ctx.send(f"{ctx.author.mention} you can't forcenick someone higher or equal to you!")
        else:
            await self.db.insert_one({
                "guild_id": ctx.guild.id,
                "user_id": member.id,
                "nickname": nickname,
                #"author": ctx.author
            })
            await member.edit(nick=nickname)
            embed2 = discord.Embed(description = f"<:check:921544057312915498> Forcenick for <@{member.id}> has been created as **{nickname}**", color=0x43B581)
            return await ctx.send(embed=embed2)

    @forcenick.command(
        aliases = ['fnr'],
        usage = "Mange_nicknames",
        description = "Remove a previously forced nickname",
        brief = "member",
        help = "```Syntax: forcenick remove [member]\nExample: forcenick remove @jacob``` "
    )
    @commands.has_permissions(manage_nicknames=True)
    async def remove(self, ctx, member:discord.Member):
        check = await self.db.find_one({ "guild_id": ctx.guild.id, "user_id": member.id})
        if check:
            embed3 = discord.Embed(description = f"<:check:921544057312915498> Forcenick for <@{member.id}> has been **removed**", color=0x43B581)
            await self.db.delete_many({ "guild_id": ctx.guild.id, "user_id": member.id})
            await member.edit(nick=None)
            return await ctx.send(embed=embed3)
        else:
            embed3 = discord.Embed(description = f"{self.urgentmoji}: No forcenick found for <@{member.id}>", color=self.urgecolor)
            return await ctx.send(embed=embed3)




async def setup(bot):
    await bot.add_cog(forceNickBud(bot))