import discord, motor.motor_asyncio, datetime
import discord, os, asyncio
from discord.ext import commands
from Core import utils

class voiceLogging(commands.Cog):
    def __init__(self, client):
        self.bot = client  
        self.onls = ['on', 'true']
        self.offls = ['off', 'false']
        self.db = self.bot.db["logging"]
        self.urgecolor = 0xF3DD6C
        self.errorcol = 0xA90F25 # error color
        self.success = discord.Colour.blurple() #theme
        self.checkmoji = "<:blurple_check:921544108252741723>" # success emoji
        self.xmoji = "<:yy_yno:921559254677200957>" # unsuccessful emoji
        self.urgentmoji = "<:n_:921559211366838282>" # exclamation emoji

    @commands.group(
        aliases = ['logs', 'logger'],
        usage = "Manage_guild",
        description = "Setup various types of logging for your server (joins, leaves, moderation, voice chats)",
        brief =  'subcommand',
        help = "```Syntax: loggging [type] <arg>\nExample: logging voice on```"
    )
    async def logging(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Command: logging", description="Setup various types of logging for your server (joins, leaves, moderation, voice chats)\n```makefile\nSyntax: loggging [type] <arg>\nExample: logging voice on\n```", color = discord.Color.blurple())
                embed.set_author(name="Logging help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('logging').walk_commands()])} ・ Logging")
                return await ctx.send(embed=embed)
        except Exception as e:
            print(e) 

    @logging.command(
        usage = "Manage_guild",
        description = "Build the logging structure for your server",
        brief = "None",
        help = "```Syntax: logging setup [channel]\nExample: logging setup #logs```"
    )
    @commands.has_permissions(manage_guild=True)
    async def setup(self, ctx, channel: discord.TextChannel):
        check = await self.db.find_one({ "guild_id": ctx.guild.id})
        if not check:
            await self.db.insert_one({
                "guild_id": ctx.guild.id,
                "channel": None,
                "voice": "on",
                "moderation": "on",
                "joins": "on",
                "leaves": "on",
            })
            msg = discord.Embed(description="<:check:921544057312915498> **Initiating** logging setup", timestamp=ctx.message.created_at, color= 0x43B581)
            msg2 = discord.Embed(description="<a:whiteloading:1006977730912464936> **Finishing up**")
            message = await ctx.send(embed=msg)
            await asyncio.sleep(1.5)
            await message.edit(embed=msg2)
            await asyncio.sleep(3)
            await self.db.update_one({ "guild_id": ctx.guild.id}, { "$set": {"channel": channel.id}})
            ms3 = discord.Embed(description=f"<:check:921544057312915498> **Logging** is now **active** and set to the channel: <#{channel.id}>", timestamp=ctx.message.created_at, color= 0x43B581)
            await message.edit(embed=ms3)
        else:
            await self.db.update_one({ "guild_id": ctx.guild.id}, { "$set": {"channel": channel.id}})
            ms3 = discord.Embed(description=f"<:check:921544057312915498> The **logging** **channel** has been updated to <#{channel.id}>", timestamp=ctx.message.created_at, color= 0x43B581)
            await ctx.send(embed=ms3)

    @logging.command(
        aliases = ['config', 'status'],
        usage = "Manage_guild",
        description = 'View your current logging configuration',
        brief = "None",
        help = "```Example: logging settings```"
    )
    @commands.has_permissions(manage_guild=True)
    async def settings(self, ctx):
        check = await self.db.find_one({ "guild_id": ctx.guild.id})
        if not check:
            ms1 = discord.Embed(description=f"{self.xmoji} The **logging module** has not been setup yet. **Please try** ``{await utils.get_prefix(self=self, bot=self.bot, ctx=ctx)}help logging setup``", color=self.errorcol)
            return await ctx.send(embed=ms1)
        else:
            channel = check['channel']
            joins = check['joins']
            if "on" in joins:
                joins = "<:check:921544057312915498>"
            else:
                joins = "<:redTick:1007263494078484611>"
            leaves = check['leaves']
            if "on" in leaves:
                leaves = "<:check:921544057312915498>"
            else:
                leaves = "<:redTick:1007263494078484611>"
            moderation = check['moderation']
            if "on" in moderation:
                moderation = "<:check:921544057312915498>"
            else:
                moderation = "<:redTick:1007263494078484611>"
            voice = check['voice']
            if "on" in voice:
                voice = "<:check:921544057312915498>"
            else:
                voice = "<:redTick:1007263494078484611>"
            embed = discord.Embed(title="Logging Configuration", timestamp=discord.utils.utcnow(), color=0x43B581)
            embed.add_field(name="__Module:__", value=f"**Log Channel:** <#{channel}>\n\n**Join logs:** {joins}\n**Leave logs:** {leaves}\n**Moderation Logs:** {moderation}\n**Voice Logs:** {voice}")
            await ctx.send(embed=embed)


            

    @logging.command(
        usage = "Manage_guild",
        description = "Log voice logs to your log channel",
        brief = 'toggle',
        help = "```Syntax: logging voice [toggle]\nExample: logging voice toggle```"
    )
    @commands.has_permissions(manage_guild=True)
    async def voice(self, ctx, toggle):
        check = await self.db.find_one({ "guild_id": ctx.guild.id})
        if check:
            checkifon = check['voice']
            channel = check['channel']
            if "on" in checkifon:
                await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "voice": "off" }} )
                embed = discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} **Voice logs** have now been **disabled** and **will no longer** send in <#{channel}>", color=0x43B581)
                return await ctx.send(embed=embed)
            else:
                await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "voice": "on" }} )
                embed = discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} **Voice logs** have now been **enabled** and will send in <#{channel}>", color=0x43B581)
                return await ctx.send(embed=embed)
        else:
            ms1 = discord.Embed(description=f"{self.xmoji} The **logging module** has not been setup yet. **Please try** ``{await utils.get_prefix(self=self, bot=self.bot, ctx=ctx)}help logging setup``", color=self.errorcol)
            return await ctx.send(embed=ms1)

    @logging.command(
        aliases = ['mods', 'mod'],
        usage = "Manage_guild",
        description = "Logs moderative actions to the logs channel",
        brief = 'toggle',
        help = "```Syntax: logging moderation [toggle]\nExample: logging moderation toggle```"
    )
    @commands.has_permissions(manage_guild=True)
    async def moderation(self, ctx, toggle):
        check = await self.db.find_one({ "guild_id": ctx.guild.id})
        if check:
            checkifon = check['moderation']
            channel = check['channel']
            if "on" in checkifon:
                await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "moderation": "off" }} )
                embed = discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} **Moderation logs** have now been **disabled** and **will no longer** send in <#{channel}>", color=0x43B581)
                return await ctx.send(embed=embed)
            else:
                await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "moderation": "on" }} )
                embed = discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} **Moderation logs** have now been **enabled** and will send in <#{channel}>", color=0x43B581)
                return await ctx.send(embed=embed)
        else:
            ms1 = discord.Embed(description=f"{self.xmoji} The **logging module** has not been setup yet. **Please try** ``{await utils.get_prefix(self=self, bot=self.bot, ctx=ctx)}help logging setup``", color=self.errorcol)
            return await ctx.send(embed=ms1)  

    @logging.command(
        usage = "Manage_guild",
        description = "Logs joins to the logs channel",
        brief = 'toggle',
        help = "```Syntax: logging joins [toggle]\nExample: logging joins toggle```"
    )
    @commands.has_permissions(manage_guild=True)
    async def joins(self, ctx, toggle):
        check = await self.db.find_one({ "guild_id": ctx.guild.id})
        if check:
            checkifon = check['joins']
            channel = check['channel']
            if "on" in checkifon:
                await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "joins": "off" }} )
                embed = discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} **Join logs** have now been **disabled** and **will no longer** send in <#{channel}>", color=0x43B581)
                return await ctx.send(embed=embed)
            else:
                await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "joins": "on" }} )
                embed = discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} **Join logs** have now been **enabled** and will send in <#{channel}>", color=0x43B581)
                return await ctx.send(embed=embed)
        else:
            ms1 = discord.Embed(description=f"{self.xmoji} The **logging module** has not been setup yet. **Please try** ``{await utils.get_prefix(self=self, bot=self.bot, ctx=ctx)}help logging setup``", color=self.errorcol)
            return await ctx.send(embed=ms1) 


    @logging.command(
        usage = "Manage_guild",
        description = "Logs leaves to the logs channel",
        brief = 'toggle',
        help = "```Syntax: logging leaves [toggle]\nExample: logging leaves toggle```"
    )
    @commands.has_permissions(manage_guild=True)
    async def leaves(self, ctx, toggle):
        check = await self.db.find_one({ "guild_id": ctx.guild.id})
        if check:
            checkifon = check['leaves']
            channel = check['channel']
            if "on" in checkifon:
                await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "leaves": "off" }} )
                embed = discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} **Leave logs** have now been **disabled** and **will no longer** send in <#{channel}>", color=0x43B581)
                return await ctx.send(embed=embed)
            else:
                await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "leaves": "on" }} )
                embed = discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} **Leave logs** have now been **enabled** and will send in <#{channel}>", color=0x43B581)
                return await ctx.send(embed=embed)
        else:
            ms1 = discord.Embed(description=f"{self.xmoji} The **logging module** has not been setup yet. **Please try** ``{await utils.get_prefix(self=self, bot=self.bot, ctx=ctx)}help logging setup``", color=self.errorcol)
            return await ctx.send(embed=ms1) 


    @commands.Cog.listener('on_voice_state_update')
    async def logger_on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        try:
            check = await self.db.find_one({ "guild_id": member.guild.id})
            if not check:
                return
            else:
                on = check['voice']
                if "on" in on:
                    channels = self.bot.get_channel(check['channel'])

                    if before.channel == None:
                        embed = discord.Embed(title='<:Voice:921574565988139018> Member Joined Voice Channel', colour=0x1CBB3D, timestamp=discord.utils.utcnow(),
                                            description=f"<@{member.id}> **joined** <#{after.channel.id}>")
                        embed.set_footer(text=f"Member ID: {member.id}")
                        await channels.send(embed=embed)

                    if after.channel == None:
                        embed = discord.Embed(title='<:Voice:921574565988139018> Member Left Voice Channel', colour=0xF50128, timestamp=discord.utils.utcnow(),
                                            description=f"<@{member.id}> **left** <#{before.channel.id}>")
                        embed.set_footer(text=f"Member ID: {member.id}")
                        await channels.send(embed=embed)

                        
                    if before.channel != after.channel:
                        embed = discord.Embed(title='<:Voice:921574565988139018> Member Moved Voice Channels', colour=0xfccf03, timestamp=discord.utils.utcnow(),
                                            description=f"<@{member.id}> **moved** from <#{before.channel.id}> to <#{after.channel.id}>")
                        embed.set_footer(text=f"Member ID: {member.id}")
                        await channels.send(embed=embed) 
                else:
                    return
        except:
            pass; return

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        try:
            check = await self.db.find_one({ "guild_id": member.guild.id})
            if not check:
                return
            else:
                on = check['leaves']
                if "on" in on:
                    try:
                        found_entry = None
                        entry=[entry async for entry in member.guild.audit_logs(action=discord.AuditLogAction.kick, limit=1, after=discord.utils.utcnow() - datetime.timedelta(seconds=3))]
                        entry=entry[0]
                        if entry.target.id == member.id:
                            found_entry = entry
                        elif not found_entry:
                            return
                        channel = self.bot.get_channel(check['channel'])
                        embed = discord.Embed(title=f"<:kick:1015398829991940156> Member Kicked:", description=f"{member} was kicked", colour=0xF50128, timestamp=discord.utils.utcnow())
                        embed.add_field(name="__User Information__", value=f"**Created At:** {discord.utils.format_dt(member.created_at, style='f')} **({discord.utils.format_dt(member.created_at, style='R')})**\n**Kicked by:** {found_entry.user}\n```makefile\nMember: {member.id}\nPerpetrator: {found_entry.user.id}```")
                        await channel.send(embed=embed)
                    except:
                        pass
                        channel = self.bot.get_channel(check['channel'])
                        embed = discord.Embed(title="<a:LEAVE:921807122042335272> Member Left:", colour=0xF50128, timestamp=discord.utils.utcnow())
                        embed.add_field(name="__User Info__", value=f"**Member:** {member}\n**Created At:** {discord.utils.format_dt(member.created_at, style='f')} **({discord.utils.format_dt(member.created_at, style='R')})**\n**Joined At:** {discord.utils.format_dt(member.joined_at, style='f')} **({discord.utils.format_dt(member.joined_at, style='R')}**)\n```makefile\nUser ID: {member.id}\n```")
                        embed.set_thumbnail(url=member.display_avatar.url)
                        await channel.send(embed=embed)
                else:
                    return
        except: pass; return

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            check = await self.db.find_one({ "guild_id": member.guild.id})
            if not check:
                return
            else:
                on = check['joins']
                if "on" in on:
                    channel = self.bot.get_channel(check['channel'])
                    embed = discord.Embed(title="<a:JOIN:921807114308030524> Member Joined:", colour=0x1CBB3D, timestamp=discord.utils.utcnow())
                    embed.add_field(name="__User Info__", value=f"**Member:** {member}\n**Created At:** {discord.utils.format_dt(member.created_at, style='f')} **({discord.utils.format_dt(member.created_at, style='R')})**\n**Joined At:** {discord.utils.format_dt(member.joined_at, style='f')} **({discord.utils.format_dt(member.joined_at, style='R')}**)\n```makefile\nUser: {member.id}\n```")
                    embed.set_thumbnail(url=member.display_avatar.url)
                    await channel.send(embed=embed)
                else:
                    return
        except:
            pass; return

    @commands.Cog.listener()
    async def on_member_unban(self, guild, member):
        try:
            check = await self.db.find_one({ "guild_id": guild.id})
            if not check:
                return
            else:
                on = check['moderation']
                if "on" in on:
                    channel = self.bot.get_channel(check['channel'])
                    #guild = member.guild
                    found_entry = None
                    entry=[entry async for entry in guild.audit_logs(action=discord.AuditLogAction.unban, limit=1, after=discord.utils.utcnow() - datetime.timedelta(seconds=3))]
                    entry=entry[0]
                    if entry.target.id == member.id:
                        found_entry = entry
                    elif not found_entry:
                        return
                    embed = discord.Embed(title=f"<:ban:921559413930729503> User Unbanned:", description=f"{member} was unbanned", colour=0xfccf03, timestamp=discord.utils.utcnow())
                    embed.add_field(name="__User Information__", value=f"**Created At:** {discord.utils.format_dt(member.created_at, style='f')} **({discord.utils.format_dt(member.created_at, style='R')})**\n**Unbanned by:** {found_entry.user}\n```makefile\nUser: {member.id}\nPerpetrator: {found_entry.user.id}```")
                    await channel.send(embed=embed)
                else:
                    return
        except: pass; return
                
    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        try:
            check = await self.db.find_one({ "guild_id": guild.id})
            if not check:
                return
            else:
                on = check['moderation']
                if "on" in on:
                    channel = self.bot.get_channel(check['channel'])
                    #guild = member.guild
                    found_entry = None
                    entry=[entry async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1, after=discord.utils.utcnow() - datetime.timedelta(seconds=3))]
                    entry=entry[0]
                    if entry.target.id == member.id:
                        found_entry = entry
                    elif not found_entry:
                        return
                    embed = discord.Embed(title=f"<:ban:921559413930729503> User Banned:", description=f"{member} was banned", colour=0xF50128, timestamp=discord.utils.utcnow())
                    embed.add_field(name="__User Information__", value=f"**Created At:** {discord.utils.format_dt(member.created_at, style='f')} **({discord.utils.format_dt(member.created_at, style='R')})**\n**Banned by:** {found_entry.user}\n```makefile\nUser: {member.id}\nPerpetrator: {found_entry.user.id}```")
                    await channel.send(embed=embed)
                else:
                    return
        except: pass; return 



async def setup(client): 
   await client.add_cog(voiceLogging(client))