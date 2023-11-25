import discord, motor, datetime, asyncio, aiohttp, time, string, random, os
from discord.ext import commands, tasks
from colorama import Fore as f
from humanfriendly import format_timespan
import Core.utils as util
from Core.utils import get_theme
from discord import app_commands

today = datetime.date.today()
d2 = today.strftime("%B %d, %Y") 
developers = [236522835089031170, 493545772718096386, 714703136270581841]

async def codeGen(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

async def AntinukeFailEmbed(member, action, guild, punishment, thumbnail):
    embed = discord.Embed(title= "Antinuke unable to take action", color=0xFC100D)
    embed.description = "A member triggered on of the **antinukes settings** but I was unable to take action due to either **missing permissions** or their top role was above **mine**"
    embed.add_field(name="Member:", value=f"{member}")
    embed.add_field(name="Action:", value=f"{action}")
    embed.add_field(name="Server:", value=f"{guild}")
    embed.add_field(name="Failed punishment:", value=f"{punishment}")
    embed.set_thumbnail(url=thumbnail)
    return embed

async def AntinukeSuccessEmbed(member, action, guild, punishment, thumbnail, limit):
    start = datetime.datetime.now() 
    embed = discord.Embed(title= "Antinuke Sucessfully Took Action <:check:921544057312915498>", color=0x43B581)
    embed.add_field(name="Member:", value=f"{member}", inline=True)
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    embed.add_field(name="Action:", value=f"{action} **|** ``{limit}/{limit}`` in ``30 seconds``", inline=True)
    embed.add_field(name="Server:", value=f"{guild}", inline=True)
    embed.add_field(name="Blame's Actions:", value=f"{punishment}", inline=True)
    embed.add_field(name="Deployed Nuke Recap", value=f"false", inline=True)
    embed.set_thumbnail(url=thumbnail)
    end = datetime.datetime.now()
    dif = end - start
    dif_micro = dif.microseconds
    dif_millis = dif.microseconds / 1000
    embed.add_field(name="Quick Scan:", value=f"```ruby\n📁 {guild}\n ↳ Time commited: {current_time}\n ↳ Responded in: {dif_millis} ms\n```", inline=False)
    
    return embed



class antiEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = self.bot.db['settings']
        self.data = self.bot.db["servers"]
        self.limits = self.bot.db['antinukeLimits']
        self.channelFind = self.bot.db['antinukeLogs']
        self.perpetrators = {} # limit count per user
        self.penalty = {} #punishments
        self.threshold = {} #db thresholds cache
        self.cache = {} #all antinuke settings
        self.events = {} #counting events
        self.clearLimit.start()
        self.clearEvents.start()
        self.cacheThresholds.start()
        self.cacheSettings.start()
        self.cachePunishments.start()
        self.db = self.bot.db['servers']
        self.db2 = self.bot.db['settings']
        self.limits = self.bot.db['antinukeLimits']
        self.logs = self.bot.db['antinukeLogs']
        self.dbbackup = self.bot.db['antinukeServersBackups']
        self.db2backup = self.bot.db['antinukeSettingsBackups']
        self.limitsbackup = self.bot.db['antinukeLimitsBackup']
        self.errorcol = 0xA90F25 # error color
        self.urgecolor = 0xF3DD6C # exclamation color
        self.success = discord.Colour.blurple() #theme
        self.checkmoji = "<:blurple_check:921544108252741723>" # success emoji
        self.xmoji = "<:yy_yno:921559254677200957>" # unsuccessful emoji
        self.urgentmoji = "<:n_:921559211366838282>" # exclamation emoji

    @tasks.loop(minutes=55)
    async def cachePunishments(self):
        getAntinukes = self.data.find({})
        guild_ids = []
        penalties = []
        admins = []
        whitelisted = []
        for i in await getAntinukes.to_list(length=999):
            get_guilds = i['guild_id']
            get_penalties = i['punishment']
            get_whitelists = i['whitelisted']
            get_admins = i['owners']
            guild_ids.append(get_guilds)
            penalties.append(get_penalties)
            admins.append(get_admins)
            whitelisted.append(get_whitelists)
        self.penalty = {guild_ids: {'penalty': penalties, 'admins': admins, 'whitelisted': whitelisted} for (guild_ids, penalties, admins, whitelisted) in zip(guild_ids, penalties, admins, whitelisted)}

    @cachePunishments.before_loop
    async def before_cachePunishments(self):
        await self.bot.wait_until_ready()
        print(f"{f.LIGHTRED_EX}[{f.RESET}{f.BLUE}(Loop Created){f.RESET}{f.LIGHTRED_EX}]{f.RESET} {f.GREEN}->{f.RESET} {f.LIGHTGREEN_EX}AntiPunishmentCache -> LISTENING...{f.RESET}")

    @tasks.loop(minutes=50)
    async def cacheThresholds(self):
        getAntinukes = self.limits.find({})
        guild_ids = []
        kicks = []
        bans = []
        role_creations = []
        role_deletions = []
        channel_deletions = []
        channel_creations = []
        webhooks= []
        everyone_pings = []
        for i in await getAntinukes.to_list(length=999):
            get_kicks = i['--kick_members']
            get_guilds = i['guild_id']
            get_webhooks = i['--create_webhooks']
            get_bans = i['--ban_members']
            get_role_creations = i['--create_roles']
            get_role_deletions = i['--delete_roles']
            get_channel_deletions = i['--delete_channels']
            get_channel_creations = i['--create_channels']
            get_everyone_pings = i['--mention_everyone']
            guild_ids.append(get_guilds)
            kicks.append(get_kicks)
            bans.append(get_bans)
            role_creations.append(get_role_creations)
            role_deletions.append(get_role_deletions)
            channel_deletions.append(get_channel_deletions)
            channel_creations.append(get_channel_creations)
            everyone_pings.append(get_everyone_pings)
            webhooks.append(get_webhooks)
        self.threshold = {guild_ids: {'--kick_members': kicks, '--ban_members': bans, '--create_roles': role_creations, '--delete_roles': role_deletions,  '--delete_channels': channel_deletions, '--create_channels': channel_creations, '--mention_everyone': everyone_pings, '--create_webhooks': webhooks} for (guild_ids, kicks, bans, role_creations, role_deletions,  channel_deletions, channel_creations, everyone_pings, webhooks) in zip(guild_ids, kicks, bans, role_creations, role_deletions, channel_deletions, channel_creations, everyone_pings, webhooks)}

    @cacheThresholds.before_loop
    async def before_cacheThresholds(self):
        await self.bot.wait_until_ready()
        print(f"{f.LIGHTRED_EX}[{f.RESET}{f.BLUE}(Loop Created){f.RESET}{f.LIGHTRED_EX}]{f.RESET} {f.GREEN}->{f.RESET} {f.LIGHTGREEN_EX}AntiThresholdCache -> LISTENING...{f.RESET}")

    @tasks.loop(minutes=60)
    async def cacheSettings(self):
        getAntinukes = self.settings.find({})
        guild_ids = []
        kicks = []
        bans = []
        role_creations = []
        role_deletions = []
        bots = []
        channel_deletions = []
        channel_creations = []
        member_updates = []
        everyone_pings = []
        for i in await getAntinukes.to_list(length=999):
            get_kicks = i['--kick_members']
            get_guilds = i['guild_id']
            get_bans = i['--ban_members']
            get_role_creations = i['--create_roles']
            get_role_deletions = i['--delete_roles']
            get_bots = i['--add_bot']
            get_channel_deletions = i['--delete_channels']
            get_channel_creations = i['--create_channels']
            get_member_updates = i['--dangerous_permission_add']
            get_everyone_pings = i['--mention_everyone']
            guild_ids.append(get_guilds)
            kicks.append(get_kicks)
            bans.append(get_bans)
            role_creations.append(get_role_creations)
            role_deletions.append(get_role_deletions)
            bots.append(get_bots)
            channel_deletions.append(get_channel_deletions)
            channel_creations.append(get_channel_creations)
            member_updates.append(get_member_updates)
            everyone_pings.append(get_everyone_pings)
        self.cache = {guild_ids: {'--kick_members': kicks, '--ban_members': bans, '--create_roles': role_creations, '--delete_roles': role_deletions, '--add_bot': bots, '--delete_channels': channel_deletions, '--create_channels': channel_creations, '--dangerous_permission_add': member_updates, '--mention_everyone': everyone_pings} for (guild_ids, kicks, bans, role_creations, role_deletions, bots, channel_deletions, channel_creations, member_updates, everyone_pings) in zip(guild_ids, kicks, bans, role_creations, role_deletions, bots, channel_deletions, channel_creations, member_updates, everyone_pings)}

    @cacheSettings.before_loop
    async def before_cacheSettings(self):
        await self.bot.wait_until_ready()
        print(f"{f.LIGHTRED_EX}[{f.RESET}{f.BLUE}(Loop Created){f.RESET}{f.LIGHTRED_EX}]{f.RESET} {f.GREEN}->{f.RESET} {f.LIGHTGREEN_EX}AntiCache -> LISTENING...{f.RESET}")

    @tasks.loop(seconds=40)
    async def clearEvents(self):
        self.events.clear()


    @clearEvents.before_loop
    async def before_clearEvents(self):
        await self.bot.wait_until_ready()
        print(f"{f.LIGHTRED_EX}[{f.RESET}{f.BLUE}(Loop Created){f.RESET}{f.LIGHTRED_EX}]{f.RESET} {f.GREEN}->{f.RESET} {f.LIGHTGREEN_EX}AntiEvents -> LISTENING...{f.RESET}")

    @tasks.loop(seconds=40)
    async def clearLimit(self):
        self.perpetrators.clear()

    @clearLimit.before_loop
    async def before_clearLimit(self):
        await self.bot.wait_until_ready()
        print(f"{f.LIGHTRED_EX}[{f.RESET}{f.BLUE}(Loop Created){f.RESET}{f.LIGHTRED_EX}]{f.RESET} {f.GREEN}->{f.RESET} {f.LIGHTGREEN_EX}Antinuke limit cache initiated and loaded{f.RESET}")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        guild = role.guild
        if not guild.me.guild_permissions.view_audit_log:
            return
        fetch_data = self.cache.get(guild.id)
        if fetch_data is not None:
            fetch_data = self.cache[guild.id]
            check = fetch_data['--delete_roles']
            if check == "Enabled":
                logs = [entry async for entry in guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds=3))]
                logs = logs[0]
                reason = "Blame Antinuke | Unauthorized member deleted role(s) while this trigger is enabled"
                whitelisted = self.penalty[guild.id]['whitelisted']
                admins = self.penalty[guild.id]['admins']
                totalroles = []
                removedroles = []
                get_limit = self.threshold[guild.id]
                if logs.user.id in whitelisted or logs.user.id in admins:
                    return
                if get_limit:
                    limit = get_limit['--delete_roles']
                else:
                    limit = 2
                try:
                    self.perpetrators[logs.user.id]
                except KeyError:
                    self.perpetrators[logs.user.id]=1
                    perpetrator = self.perpetrators[logs.user.id]
                perpetrator = self.perpetrators[logs.user.id]
                self.perpetrators[logs.user.id]=self.perpetrators[logs.user.id]+1
                if perpetrator > limit:
                    penalty = self.penalty[guild.id]['penalty']
                    try:
                        if "ban" in penalty:
                            try:
                                await logs.user.ban(reason=reason)
                            except: pass; return
                            await asyncio.sleep(1.5)
                            logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                            if logChannel:
                                channels = logChannel['channel']
                                channel = self.bot.get_channel(channels)
                                if channel == None:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_user(channels)
                                return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action="Deleted too many roles", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                            else:
                                pass
                        elif "kick" in penalty:
                            await logs.user.kick(reason=reason)
                            await asyncio.sleep(1.5)
                            logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                            if logChannel:
                                channels = logChannel['channel']
                                channel = self.bot.get_channel(channels)
                                if channel == None:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_user(channels)
                                return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action="Deleted too many roles", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                            else:
                                pass
                        elif "strip-roles" in penalty:
                            roles = [i for i in logs.user.roles if not i.is_assignable()]
                            await logs.user.edit(roles=roles, reason=reason)
                            logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                            if logChannel:
                                channels = logChannel['channel']
                                channel = self.bot.get_channel(channels)
                                if channel == None:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_user(channels)
                                return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action="Deleted too many roles", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                            else:
                                pass
                                            #return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action="Deleted too many roles", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                        else:
                            pass
                    except Exception as e:
                        print(e)
                        #return await guild.owner.send(embed=await AntinukeFailEmbed(member=f"{logs.user}", action="Role Delete", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
            else:
                return
        else:
            return

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        guild = role.guild
        if not guild.me.guild_permissions.view_audit_log:
            return
        fetch_data = self.cache.get(guild.id)
        if fetch_data is not None:
            fetch_data = self.cache[guild.id]
            check = fetch_data['--create_roles']
            if check == "Enabled":
                logs = [entry async for entry in guild.audit_logs(action=discord.AuditLogAction.role_create, limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds=3))]
                logs = logs[0]
                reason = "Blame Antinuke | Unauthorized member created role(s) while this trigger is enabled"
                whitelisted = self.penalty[guild.id]['whitelisted']
                admins = self.penalty[guild.id]['admins']
                totalroles = []
                removedroles = []
                get_limit = self.threshold[guild.id]
                if logs.user.id in whitelisted or logs.user.id in admins:
                    return
                if get_limit:
                    limit = get_limit['--create_roles']
                else:
                    limit = 2
                try:
                    self.perpetrators[logs.user.id]
                except KeyError:
                    self.perpetrators[logs.user.id]=1
                    perpetrator = self.perpetrators[logs.user.id]
                perpetrator = self.perpetrators[logs.user.id]
                self.perpetrators[logs.user.id]=self.perpetrators[logs.user.id]+1
                if perpetrator > limit:

                    penalty = self.penalty[guild.id]['penalty']
                    try:
                        if "ban" in penalty:
                            try:
                                await logs.user.ban(reason=reason)
                            except: pass; return
                            await asyncio.sleep(1.5)
                            logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                            if logChannel:
                                channels = logChannel['channel']
                                channel = self.bot.get_channel(channels)
                                if channel == None:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_user(channels)
                                return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                            else:
                                pass
                        elif "kick" in penalty:
                            await logs.user.kick(reason=reason)
                            await asyncio.sleep(1.5)
                            logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                            if logChannel:
                                channels = logChannel['channel']
                                channel = self.bot.get_channel(channels)
                                if channel == None:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_user(channels)
                                return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                            else:
                                pass
                        elif "strip-roles" in penalty:
                            roles = [i for i in logs.user.roles if not i.is_assignable()]
                            await logs.user.edit(roles=roles, reason=reason)
                            logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                            if logChannel:
                                channels = logChannel['channel']
                                channel = self.bot.get_channel(channels)
                                if channel == None:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_user(channels)
                                return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                            else:
                                pass
                    except Exception as e:
                        print(e)
                        #return await guild.owner.send(embed=await AntinukeFailEmbed(member=f"{logs.user}", action="Role Create", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
            else:
                return
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            if member.bot:
                guild = member.guild
                if not guild.me.guild_permissions.view_audit_log:
                    return
                fetch_data = self.cache.get(guild.id)
                if fetch_data is not None:
                    fetch_data = self.cache[guild.id]
                    check = fetch_data['--add_bot']
                    if check == "Enabled":
                        logs = [entry async for entry in guild.audit_logs(action=discord.AuditLogAction.bot_add, limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds=3))]
                        logs = logs[0]
                        whitelisted = self.penalty[guild.id]['whitelisted']
                        admins = self.penalty[guild.id]['admins']
                        penalty = self.penalty[guild.id]['penalty']
                        if member.id in whitelisted or member.id in admins and logs.user.id in whitelisted or logs.user.id in admins: 
                            return
                        if member.id in whitelisted or member.id in admins and not logs.user.id in whitelisted or not logs.user.id in admins: # if the bot is whitelisted and the inviter isn't
                            # if the bots id is whitelisted and the inviters isnt
                            # logs = inviter, member= bot
                            reason = "Blame Antinuke | Unauthorized member added a whitelisted bot while the member was not whitelisted to do so. You must whitelist the bot AND member"
                            try:
                                if "ban" in penalty:
                                    try:
                                        await logs.user.ban(reason=reason)
                                    except: pass; return
                                    await asyncio.sleep(1.5)
                                    logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                                    if logChannel:
                                        channels = logChannel['channel']
                                        channel = self.bot.get_channel(channels)
                                        if channel == None:
                                            channels = logChannel['channel']
                                            channel = self.bot.get_user(channels)
                                        return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
                                    else:
                                        pass
                                elif "kick" in penalty:
                                    await logs.user.kick(reason=reason)
                                    await asyncio.sleep(1.5)
                                    if logChannel:
                                        channels = logChannel['channel']
                                        channel = self.bot.get_channel(channels)
                                        if channel == None:
                                            channels = logChannel['channel']
                                            channel = self.bot.get_user(channels)
                                        return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
                                    else:
                                        pass
                
                                elif "strip-roles" in penalty:
                                    roles = [i for i in logs.user.roles if not i.is_assignable()]
                                    await logs.user.edit(roles=roles, reason=reason)
                                    if logChannel:
                                        channels = logChannel['channel']
                                        channel = self.bot.get_channel(channels)
                                        if channel == None:
                                            channels = logChannel['channel']
                                            channel = self.bot.get_user(channels)
                                        return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
                                    else:
                                        pass
                            except Exception as e:
                                print(e)
                                #return await guild.owner.send(embed=await AntinukeFailEmbed(member=f"{logs.user}", action="Added a whitelisted bot without being permitted to do so.", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
                        if not member.id in whitelisted or not member.id in admins and logs.user.id in whitelisted or logs.user.id in admins:
                            # if member (bot) isnt whitelisted and inviter is 
                            reason = "Blame Antinuke | Unwhitelisted bot was added by a whitelisted user (Must whitelist both)"
                            try:
                                if "ban" in penalty:
                                    try:
                                        await member.ban(reason=reason)
                                    except: pass; return
                                    await asyncio.sleep(1.5)
                                    if logChannel:
                                        channels = logChannel['channel']
                                        channel = self.bot.get_channel(channels)
                                        if channel == None:
                                            channels = logChannel['channel']
                                            channel = self.bot.get_user(channels)
                                        return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
                                    else:
                                        pass
                                elif "kick" in penalty:
                                    await member.kick(reason=reason)
                                    await asyncio.sleep(1.5)
                                    if logChannel:
                                        channels = logChannel['channel']
                                        channel = self.bot.get_channel(channels)
                                        if channel == None:
                                            channels = logChannel['channel']
                                            channel = self.bot.get_user(channels)
                                        return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
                                    else:
                                        pass
                                elif "strip-roles" in penalty:
                                    await member.kick(reason="Blame Antinuke | Unwhitelisted bot was added by a whitelisted user (Must whitelist both) [Was unable to strip the bots staff so kicked instead.]")
                                    await asyncio.sleep(1.5)
                                    if logChannel:
                                        channels = logChannel['channel']
                                        channel = self.bot.get_channel(channels)
                                        if channel == None:
                                            channels = logChannel['channel']
                                            channel = self.bot.get_user(channels)
                                        return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
                                    else:
                                        pass
                            except Exception as e:
                                print(e)
                            # return await guild.owner.send(embed=await AntinukeFailEmbed(member=f"{logs.user}", action="A whitelisted user added an **unwhitelisted** bot", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon)) 
                        if not member.id in whitelisted or not member.id in admins and not logs.user.id in whitelisted or not logs.user.id in admins: 
                            # if member isnt whitelisted and bot isnt   
                            reason = "Blame Antinuke | Unauthorized member added an unauthorized bot"
                            try:
                                if "ban" in penalty:
                                    try:
                                        await logs.user.ban(reason=reason)
                                        await member.ban(reason=reason)
                                    except: pass; return
                                    await asyncio.sleep(1.5)
                                    if logChannel:
                                        channels = logChannel['channel']
                                        channel = self.bot.get_channel(channels)
                                        if channel == None:
                                            channels = logChannel['channel']
                                            channel = self.bot.get_user(channels)
                                        return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
                                    else:
                                        pass
                                elif "kick" in penalty:
                                    await logs.user.kick(reason=reason)
                                    await member.kick(reason=reason)
                                    await asyncio.sleep(1.5)
                                    if logChannel:
                                        channels = logChannel['channel']
                                        channel = self.bot.get_channel(channels)
                                        if channel == None:
                                            channels = logChannel['channel']
                                            channel = self.bot.get_user(channels)
                                        return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
                                    else:
                                        pass
                                elif "strip-roles" in penalty:
                                    await member.kick(reason="Blame Antinuke | Unauthorized member added an unauthorized bot (Was unable to strip roles from the bot so kicked instead)")
                                    if logChannel:
                                        channels = logChannel['channel']
                                        channel = self.bot.get_channel(channels)
                                        if channel == None:
                                            channels = logChannel['channel']
                                            channel = self.bot.get_user(channels)
                                        return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
                                    else:
                                        pass
                            except Exception as e:
                                print(e)
                                #return await guild.owner.send(embed=await AntinukeFailEmbed(member=f"{logs.user}", action="An unwhitelisted bot was added by an unwhitelisted member", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))   
                else:
                    return
            else:
                return
        except:
            pass; return
                

                
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        if not guild.me.guild_permissions.view_audit_log:
            return
        fetch_data = self.cache.get(guild.id)
        if fetch_data is not None:
            fetch_data = self.cache[guild.id]
            check = fetch_data['--kick_members']
            if check == "Enabled":
                logs = [entry async for entry in guild.audit_logs(action=discord.AuditLogAction.kick, limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds=3))]
                try:
                    logs = logs[0]
                except IndexError:
                    return
                reason = "Blame Antinuke | Unauthorized member kicked another member while this trigger is enabled"
                whitelisted = self.penalty[guild.id]['whitelisted']
                admins = self.penalty[guild.id]['admins']
                totalroles = []
                removedroles = []
                get_limit = self.threshold[guild.id]
                if logs.user.id in whitelisted or logs.user.id in admins:
                    return
                if get_limit:
                    limit = get_limit['--kick_members']
                else:
                    limit = 2
                try:
                    self.perpetrators[logs.user.id]
                except KeyError:
                    self.perpetrators[logs.user.id]=1
                    perpetrator = self.perpetrators[logs.user.id]
                perpetrator = self.perpetrators[logs.user.id]
                self.perpetrators[logs.user.id]=self.perpetrators[logs.user.id]+1 
                if perpetrator > limit:
                    penalty = self.penalty[guild.id]['penalty']
                    try:
                        if "ban" in penalty:
                            try:
                                await logs.user.ban(reason=reason)
                            except: pass; return
                            await asyncio.sleep(1.5)
                            logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                            if logChannel:
                                channels = logChannel['channel']
                                channel = self.bot.get_channel(channels)
                                if channel == None:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_user(channels)
                                return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                            else:
                                pass
                        elif "kick" in penalty:
                            await logs.user.kick(reason=reason)
                            await asyncio.sleep(1.5)
                            logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                            if logChannel:
                                channels = logChannel['channel']
                                channel = self.bot.get_channel(channels)
                                if channel == None:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_user(channels)
                                return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                            else:
                                pass
                        elif "strip-roles" in penalty:
                            roles = [i for i in logs.user.roles if not i.is_assignable()]
                            await logs.user.edit(roles=roles, reason=reason)
                            logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                            if logChannel:
                                channels = logChannel['channel']
                                channel = self.bot.get_channel(channels)
                                if channel == None:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_user(channels)
                                return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                            else:
                                pass
                    except:
                        pass; return
                    # return await guild.owner.send(embed=await AntinukeFailEmbed(member=f"{logs.user}", action="Kicked Member", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
                else:
                    return
            else:
                return    
        else:
            return  


    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        if not guild.me.guild_permissions.view_audit_log:
            return
        fetch_data = self.cache.get(guild.id)
        if fetch_data is not None:
            fetch_data = self.cache[guild.id]
            check = fetch_data['--ban_members']
            if check == "Enabled":
                logs = [entry async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds=3))]
                logs = logs[0]
                reason = "Blame Antinuke | Unauthorized member banned another member while this trigger is enabled"
                whitelisted = self.penalty[guild.id]['whitelisted']
                admins = self.penalty[guild.id]['admins']
                totalroles = []
                removedroles = []
                get_limit = self.threshold[guild.id]
                if logs.user.id in whitelisted or logs.user.id in admins:
                    return
                if get_limit:
                    limit = get_limit['--ban_members']
                else:
                    limit = 2
                try:
                    self.perpetrators[logs.user.id]
                except KeyError:
                    self.perpetrators[logs.user.id]=1
                    perpetrator = self.perpetrators[logs.user.id]
                perpetrator = self.perpetrators[logs.user.id]
                self.perpetrators[logs.user.id]=self.perpetrators[logs.user.id]+1
                if perpetrator > limit:
                    penalty = self.penalty[guild.id]['penalty']
                    try:
                        if "ban" in penalty:
                            try:
                                await logs.user.ban(reason=reason)
                            except: pass; return
                            await asyncio.sleep(1.5)
                            logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                            if logChannel:
                                channels = logChannel['channel']
                                channel = self.bot.get_channel(channels)
                                if channel == None:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_user(channels)
                                return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                            else:
                                pass
                        elif "kick" in penalty:
                            await logs.user.kick(reason=reason)
                            await asyncio.sleep(1.5)
                            logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                            if logChannel:
                                channels = logChannel['channel']
                                channel = self.bot.get_channel(channels)
                                if channel == None:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_user(channels)
                                return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                            else:
                                pass
                        elif "strip-roles" in penalty:
                            roles = [i for i in logs.user.roles if not i.is_assignable()]
                            await logs.user.edit(roles=roles, reason=reason)
                            logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                            if logChannel:
                                channels = logChannel['channel']
                                channel = self.bot.get_channel(channels)
                                if channel == None:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_user(channels)
                                return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                            else:
                                pass
                    except Exception as e:
                        print(e)
                        #await member.kick(reason="Could not strip roles, force kicked.")
                        #return await guild.owner.send(embed=await AntinukeFailEmbed(member=f"{logs.user}", action="Banned Member", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
                else:
                    return
            else:
                return   
        else:
            return


    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        guild = channel.guild
        if not guild.me.guild_permissions.view_audit_log:
            return
        fetch_data = self.cache.get(guild.id)
        if fetch_data is not None:
            fetch_data = self.cache[guild.id]
            check = fetch_data['--delete_channels']
            if check == "Enabled":
                logs = [entry async for entry in guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds=3))]
                logs = logs[0]
                reason = "Blame Antinuke | Unauthorized member deleted channels while this trigger is enabled"
                whitelisted = self.penalty[guild.id]['whitelisted']
                admins = self.penalty[guild.id]['admins']
                totalroles = []
                removedroles = []
                get_limit = self.threshold[guild.id]
                if logs.user.id in whitelisted or logs.user.id in admins:
                    return
                if get_limit:
                    limit = get_limit['--delete_channels']
                else:
                    limit = 2
                try:
                    self.perpetrators[logs.user.id]
                except KeyError:
                    self.perpetrators[logs.user.id]=1
                    perpetrator = self.perpetrators[logs.user.id]
                perpetrator = self.perpetrators[logs.user.id]
                self.perpetrators[logs.user.id]=self.perpetrators[logs.user.id]+1
                if perpetrator > limit:
                    penalty = self.penalty[guild.id]['penalty']
                    try:
                        if "ban" in penalty:
                            try:
                                await logs.user.ban(reason=reason)
                            except: pass; return
                            await asyncio.sleep(1.5)
                            logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                            if logChannel:
                                channels = logChannel['channel']
                                channel = self.bot.get_channel(channels)
                                if channel == None:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_user(channels)
                                return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                            else:
                                pass
                        elif "kick" in penalty:
                            await logs.user.kick(reason=reason)
                            await asyncio.sleep(1.5)
                            logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                            if logChannel:
                                channels = logChannel['channel']
                                channel = self.bot.get_channel(channels)
                                if channel == None:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_user(channels)
                                return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                            else:
                                pass
                        elif "strip-roles" in penalty:
                            roles = [i for i in logs.user.roles if not i.is_assignable()]
                            await logs.user.edit(roles=roles, reason=reason)
                            logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                            if logChannel:
                                channels = logChannel['channel']
                                channel = self.bot.get_channel(channels)
                                if channel == None:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_user(channels)
                                return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                            else:
                                pass
                    except Exception as e:
                        print(e)
                    # await logs.user.kick(reason="Could not strip roles, force kicked.")
                    # return await guild.owner.send(embed=await AntinukeFailEmbed(member=f"{logs.user}", action="Channel Delete", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
                else:
                    return
            else:
                return
        else:
            return


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        try:
            guild = before.guild
            if not guild.me.guild_permissions.view_audit_log:
                return
            fetch_data = self.cache.get(guild.id)
            if fetch_data is not None:
                fetch_data = self.cache[guild.id]
                check = fetch_data['--dangerous_permission_add']
                if check == "Enabled":
                    logs = [entry async for entry in guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds=3))]
                    logs = logs[0]
                    reason = "Blame Antinuke | Unauthorized member added a role with dangerous permissions to another member while this trigger is enabled"
                    whitelisted = self.penalty[guild.id]['whitelisted']
                    admins = self.penalty[guild.id]['admins']
                    totalroles = []
                    removedroles = []
                    if logs.user.id in whitelisted or logs.user.id in admins or logs.user.id == logs.target.id:
                        return
                    try:
                        newRole = next(role for role in after.roles if role not in before.roles)
                    except StopIteration:
                        return
                    penalty = self.penalty[guild.id]['penalty']
                    try:
                        if newRole.permissions.ban_members or newRole.permissions.administrator or newRole.permissions.manage_guild or newRole.permissions.manage_channels or newRole.permissions.manage_roles or newRole.permissions.mention_everyone or newRole.permissions.manage_webhooks:
                            if "ban" in penalty:
                                await logs.target.remove_roles(newRole, reason=reason)
                                try:
                                    await logs.user.ban(reason=reason)
                                except: pass; return
                                await asyncio.sleep(1.5)
                                logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                                if logChannel:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_channel(channels)
                                    if channel == None:
                                        channels = logChannel['channel']
                                        channel = self.bot.get_user(channels)
                                    return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit="``N/A``"))
                                else:
                                    pass
                            elif "kick" in penalty:
                                await logs.target.remove_roles(newRole, reason=reason)
                                await logs.user.kick(reason=reason)
                                await asyncio.sleep(1.5)
                                logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                                if logChannel:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_channel(channels)
                                    if channel == None:
                                        channels = logChannel['channel']
                                        channel = self.bot.get_user(channels)
                                    return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit="``N/A``"))
                                else:
                                    pass
                            elif "strip-roles" in penalty:
                                roles = [i for i in logs.user.roles if not i.is_assignable()]
                                await logs.target.remove_roles(newRole, reason=reason)
                                await logs.user.edit(roles=roles, reason=reason)
                                logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                                if logChannel:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_channel(channels)
                                    if channel == None:
                                        channels = logChannel['channel']
                                        channel = self.bot.get_user(channels)
                                    return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit="``N/A``"))
                                else:
                                    pass
                    except Exception as e:
                        print(e)
                        #await logs.user.kick(reason="Could not strip roles, force kicked.")
                        #return await guild.owner.send(embed=await AntinukeFailEmbed(member=f"{logs.user}", action="Dangerous Permission Add", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
                else:
                    return
            else:
                return
        except:
            pass; return

    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        guild = channel.guild
        if not guild.me.guild_permissions.view_audit_log:
            return
        fetch_data = self.cache.get(guild.id)
        if fetch_data is not None:
            fetch_data = self.cache[guild.id]
            check = fetch_data['--create_channels']
            if check == "Enabled":
                logs = [entry async for entry in guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds=3))]
                logs = logs[0]
                reason = "Blame Antinuke | Unauthorized member created channels while this trigger is enabled"
                whitelisted = self.penalty[guild.id]['whitelisted']
                admins = self.penalty[guild.id]['admins']
                totalroles = []
                removedroles = []
                get_limit = self.threshold[guild.id]
                if logs.user.id in whitelisted or logs.user.id in admins:
                    return
                if get_limit:
                    limit = get_limit['--create_channels']
                else:
                    limit = 2
                try:
                    self.perpetrators[logs.user.id]
                except KeyError:
                    self.perpetrators[logs.user.id]=1
                    perpetrator = self.perpetrators[logs.user.id]
                perpetrator = self.perpetrators[logs.user.id]
                self.perpetrators[logs.user.id]=self.perpetrators[logs.user.id]+1
                if perpetrator > limit:
                    penalty = self.penalty[guild.id]['penalty']
                    try:
                        if "ban" in penalty:
                            try:
                                await logs.user.ban(reason=reason)
                            except: pass; return
                            await asyncio.sleep(1.5)
                            logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                            if logChannel:
                                channels = logChannel['channel']
                                channel = self.bot.get_channel(channels)
                                if channel == None:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_user(channels)
                                return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                            else:
                                pass
                        elif "kick" in penalty:
                            await logs.user.kick(reason=reason)
                            await asyncio.sleep(1.5)
                            logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                            if logChannel:
                                channels = logChannel['channel']
                                channel = self.bot.get_channel(channels)
                                if channel == None:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_user(channels)
                                return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                            else:
                                pass
                        elif "strip-roles" in penalty:
                            roles = [i for i in logs.user.roles if not i.is_assignable()]
                            await logs.user.edit(roles=roles, reason=reason)
                            logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                            if logChannel:
                                channels = logChannel['channel']
                                channel = self.bot.get_channel(channels)
                                if channel == None:
                                    channels = logChannel['channel']
                                    channel = self.bot.get_user(channels)
                                return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{logs.user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                            else:
                                pass
                    except Exception as e:
                        print(e)
                        #await logs.user.kick(reason="Could not strip roles, force kicked.")
                        #return await guild.owner.send(embed=await AntinukeFailEmbed(member=f"{logs.user}", action="Channel Create", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
            
                else:
                    return
            else:
                return
        else:
            return

    
    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            guild = message.guild
            if not guild.me.guild_permissions.view_audit_log:
                return
            if "@everyone" in message.content.lower() and self.bot.user.mentioned_in(message):
                fetch_data = self.cache.get(guild.id)

                if fetch_data is not None:
                    fetch_data = self.cache[guild.id]
                    check = fetch_data['--mention_everyone']
                    if check == "Enabled":
                        reason = "Blame Antinuke | Unauthorized member tried pinging members while this trigger is active"
                        whitelisted = self.penalty[guild.id]['whitelisted']
                        admins = self.penalty[guild.id]['admins']
                        totalroles = []
                        removedroles = []
                        get_limit = self.threshold[guild.id]
                        if message.author in whitelisted or message.author in admins:
                            return
                        if get_limit:
                            limit = get_limit['--mention_everyone']
                        else:
                            limit = 2
                        try:
                            self.perpetrators[message.author.id]
                        except KeyError:
                            self.perpetrators[message.author.id]=1
                            perpetrator = self.perpetrators[message.author.id]
                        perpetrator = self.perpetrators[message.author.id]
                        self.perpetrators[message.author.id]=self.perpetrators[message.author.id]+1
                        if perpetrator > limit:
                            penalty = self.penalty[guild.id]['penalty']
                            user = self.bot.get_user(message.author.id)
                            try:
                                if "ban" in penalty:
                                    await guild.ban(user, reason=f"{reason}")
                                    await asyncio.sleep(1.5)
                                    logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                                    if logChannel:
                                        channels = logChannel['channel']
                                        channel = self.bot.get_channel(channels)
                                        if channel == None:
                                            channels = logChannel['channel']
                                            channel = self.bot.get_user(channels)
                                        return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                                    else:
                                        pass
                                elif "kick" in penalty:
                                    await guild.kick(user, reason=f"{reason}")
                                    await asyncio.sleep(1.5)
                                    logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                                    if logChannel:
                                        channels = logChannel['channel']
                                        channel = self.bot.get_channel(channels)
                                        if channel == None:
                                            channels = logChannel['channel']
                                            channel = self.bot.get_user(channels)
                                        return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                                    else:
                                        pass
                                elif "strip-roles" in penalty:
                                    roles = [i for i in message.author.roles if not i.is_assignable()]
                                    await message.author.edit(roles=roles, reason=reason)
                                    logChannel = await self.channelFind.find_one({ "guild_id": guild.id})
                                    if logChannel:
                                        channels = logChannel['channel']
                                        channel = self.bot.get_channel(channels)
                                        if channel == None:
                                            channels = logChannel['channel']
                                            channel = self.bot.get_user(channels)
                                        return await channel.send(embed=await AntinukeSuccessEmbed(member=f"{user}", action=reason, guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon, limit=str(limit)))
                                    else:
                                        pass
                            except Exception as e:
                                print(e)
                                #await message.author.kick(reason="Could not strip roles, force kicked.")
                            # return await guild.owner.send(embed=await AntinukeFailEmbed(member=f"{message.author}", action="Member tried pinging @everyone", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
                        else:
                            return
                    else:
                        return
                else:
                    return
            else:
                return
        except:
            pass; return


    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        guild = before
        if not guild.me.guild_permissions.view_audit_log:
            return
        try:
            self.events[guild.id]
        except KeyError:
            self.events[guild.id] = 1
        self.events[guild.id] = self.events[guild.id]+1
        fetch_data = await self.data.find_one({ "guild_id": guild.id })
        if fetch_data and not self.events[guild.id] >= 10:
            bannerlogs = [entry async for entry in guild.audit_logs(action=discord.AuditLogAction.guild_update, limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds=3))]
            bannerlogs = bannerlogs[0]
            bannerreason = "Blame Antinuke | Unauthorized member tried changing the guilds banner while this trigger is enabled"
            whitelisted = fetch_data['whitelisted']
            admins = fetch_data['owners']
            get = await self.settings.find_one({ "guild_id": guild.id})
            bannercheck = get['--change_guild_banner']
            iconcheck = get['--change_guild_icon']
            namecheck = get['--change_guild_name']
            vericheck = get['--change_guild_verification']
            rulecheck = get['--change_guild_rules']
            vanitycheck = get['--change_guild_vanity']
            #vani = await self.data.find_one({ "guild_id": guild.id})
            try:
                if before.banner.url != after.banner.url:
                    if bannercheck == "Enabled":
                        if bannerlogs.user.id in whitelisted or bannerlogs.user.id in admins:
                            return
                        penalty = fetch_data['punishment']
                        try:
                            if "ban" in penalty:
                                try:
                                    await bannerlogs.user.ban(reason=bannerreason)
                                except: pass; return
                                await asyncio.sleep(1.5)
                            elif "kick" in penalty:
                                await bannerlogs.user.kick(reason=bannerreason)
                                await asyncio.sleep(1.5)
                            elif "strip-roles" in penalty:
                               roles = [i for i in bannerlogs.user.roles if not i.is_assignable()]
                               return await bannerlogs.user.edit(roles=roles, reason=bannerreason)
                        except Exception as e:
                            print(e)
                            #await bannerlogs.kick(reason="Could not strip roles, force kicked.")
                            #return await guild.owner.send(embed=await AntinukeFailEmbed(member=f"{bannerlogs.user}", action="Banner Change", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
            except:
                pass
            try:
                if before.icon.url != after.icon.url:
                    if iconcheck == "Enabled":
                        iconlogs= [entry async for entry in guild.audit_logs(action=discord.AuditLogAction.guild_update, limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds=3))]
                        iconlogs = iconlogs[0]
                        iconreason = "Blame Antinuke | Unauthorized member tried changing the guilds icon while this trigger is enabled"
                        if iconlogs.user.id in whitelisted or iconlogs.user.id in admins:
                            return
                        penalty = fetch_data['punishment']
                        try:
                            if "ban" in penalty:
                                await iconlogs.user.ban(reason=iconreason)
                                #try:
                                   # await guild.edit(icon=await guild.icon.read())
                                #except:
                                  #  pass
                                return await asyncio.sleep(1.5)
                            elif "kick" in penalty:
                                await iconlogs.user.kick(reason=iconreason)
                                #try:
                                  #  await guild.edit(icon=await guild.icon.read())
                               # except:
                                  #  pass
                                return await asyncio.sleep(1.5)
                            elif "strip-roles" in penalty:
                                try:
                                    await guild.edit(icon=await guild.icon.read())
                                except:
                                    pass
                                roles = [i for i in iconlogs.user.roles if not i.is_assignable()]
                                return await iconlogs.user.edit(roles=roles, reason=iconreason)
                        except Exception as e:
                            print(e)
                           #await iconlogs.kick(reason="Could not strip roles, force kicked.")
                            #return await guild.owner.send(embed=await AntinukeFailEmbed(member=f"{iconlogs.user}", action="Icon Change", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
            except:
                pass
            try:
                if before.name != after.name:
                    if namecheck == "Enabled":
                        namelogs= [entry async for entry in guild.audit_logs(action=discord.AuditLogAction.guild_update, limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds=3))]
                        namelogs = namelogs[0]
                        namereason = "Blame Antinuke | Unauthorized member tried changing the guilds name while this trigger is enabled"
                        if namelogs.user.id in whitelisted or namelogs.user.id in admins:
                            return
                        penalty = fetch_data['punishment']
                        try:
                            if "ban" in penalty:
                                await namelogs.user.ban(reason=namereason)
                                #try:
                                #    await guild.edit(name=guild.name)
                               # except:
                                #    pass
                                return await asyncio.sleep(1.5)
                            elif "kick" in penalty:
                                await namelogs.user.kick(reason=namereason)
                               # try:
                                 #   await guild.edit(name=guild.name)
                               # except:
                               #     pass
                                return await asyncio.sleep(1.5)
                            elif "strip-roles" in penalty:
                               # try:
                              #      await guild.edit(name=guild.name)
                               # except:
                               #     pass
                               roles = [i for i in namelogs.user.roles if not i.is_assignable()]
                               return await namelogs.user.edit(roles=roles, reason=namereason)
                        except Exception as e:
                            print(e)
                            #await namelogs.kick(reason="Could not strip roles, force kicked.")
                            #return await guild.owner.send(embed=await AntinukeFailEmbed(member=f"{namelogs.user}", action="Changed guilds name", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
            except:
                pass
            try:
                if before.verification_level.value != after.verification_level.value:
                    if vericheck == "Enabled":
                        verilogs= [entry async for entry in guild.audit_logs(action=discord.AuditLogAction.guild_update, limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds=3))]
                        verilogs = verilogs[0]
                        verireason = "Blame Antinuke | Unauthorized member tried changing the guilds verification level while this trigger is enabled"
                        if verilogs.user.id in whitelisted or verilogs.user.id in admins:
                            return
                        penalty = fetch_data['punishment']
                        try:
                            if "ban" in penalty:
                                await verilogs.user.ban(reason=verireason)
                                #try:
                                #    await guild.edit(name=guild.name)
                               # except:
                                #    pass
                                return await asyncio.sleep(1.5)
                            elif "kick" in penalty:
                                await verilogs.user.kick(reason=verireason)
                               # try:
                                 #   await guild.edit(name=guild.name)
                               # except:
                               #     pass
                                return await asyncio.sleep(1.5)
                            elif "strip-roles" in penalty:
                               # try:
                              #      await guild.edit(name=guild.name)
                               # except:
                               #     pass
                               roles = [i for i in verilogs.user.roles if not i.is_assignable()]
                               return await verilogs.user.edit(roles=roles, reason=verireason)
                        except Exception as e:
                            print(e)
                           # await verilogs.kick(reason="Could not strip roles, force kicked.")
                            #return await guild.owner.send(embed=await AntinukeFailEmbed(member=f"{verilogs.user}", action="Changed verification level", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))
            except:
                pass
            try:
                if before.rules_channel.id != after.rules_channel.id or before.rules_channel.id and after.rules_channel.id == None:
                    if rulecheck == "Enabled":
                        rulelogs= [entry async for entry in guild.audit_logs(action=discord.AuditLogAction.guild_update, limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds=3))]
                        rulelogs = rulelogs[0]
                        rulereason = "Blame Antinuke | Unauthorized member tried changing the guilds rules channel while this trigger is enabled"
                        if rulelogs.user.id in whitelisted or rulelogs.user.id in admins:
                            return
                        penalty = fetch_data['punishment']
                        try:
                            if "ban" in penalty:
                                await rulelogs.user.ban(reason=rulereason)
                                #try:
                                #    await guild.edit(name=guild.name)
                               # except:
                                #    pass
                                return await asyncio.sleep(1.5)
                            elif "kick" in penalty:
                                await rulelogs.user.kick(reason=rulereason)
                               # try:
                                 #   await guild.edit(name=guild.name)
                               # except:
                               #     pass
                                return await asyncio.sleep(1.5)
                            elif "strip-roles" in penalty:
                               roles = [i for i in rulelogs.user.roles if not i.is_assignable()]
                               return await rulelogs.user.edit(roles=roles, reason=rulereason)
                        except Exception as e:
                            print(e)
                            #await rulelogs.kick(reason="Could not strip roles, force kicked.")
                            #return await guild.owner.send(embed=await AntinukeFailEmbed(member=f"{rulelogs.user}", action="Changed guilds rules", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))  
            except:
                pass  
            try:

                if before.vanity_invite != after.vanity_invite:
                    if vanitycheck == "Enabled":
                        vanitylogs= [entry async for entry in guild.audit_logs(action=discord.AuditLogAction.guild_update, limit=1, after=datetime.datetime.now() - datetime.timedelta(seconds=3))]
                        vanitylogs = vanitylogs[0]
                        vanity_url_before: discord.AuditLogDiff = vanitylogs.before
                        vanity_url: str = vanity_url_before.vanity_url_code
                        vanity_url_after: discord.AuditLogDiff = vanitylogs.after
                        after_url: str = vanity_url_after.vanity_url_code
                        vanityreason = "Blame Antinuke | Unauthorized member tried changing the guilds vanity while this trigger is enabled"
                        if vanitylogs.user.id in whitelisted or vanitylogs.user.id in admins:
                            return
                        penalty = fetch_data['punishment']
                        try:
                            if "ban" in penalty:
                                try:
                                    await guild.edit(vanity_code=vanity_url, reason=f"Blame Antinuke | Reverted the Vanity URL back to its previous state.")
                                except:
                                    pass
                                await vanitylogs.user.ban(reason=vanityreason)
                                #try:
                                #    await guild.edit(name=guild.name)
                               # except:
                                #    pass
                                return await asyncio.sleep(1.5)
                            elif "kick" in penalty:
                                try:
                                    await guild.edit(vanity_code=vanity_url, reason=f"Blame Antinuke | Reverted the Vanity URL back to its previous state.")
                                except:
                                    pass
                                await vanitylogs.user.kick(reason=vanityreason)
                               # try:
                                 #   await guild.edit(name=guild.name)
                               # except:
                               #     pass
                                return await asyncio.sleep(1.5)
                            elif "strip-roles" in penalty:
                                try:
                                    await guild.edit(vanity_code=vanity_url, reason=f"Blame Antinuke | Reverted the Vanity URL back to its previous state.")
                                except:
                                    pass
                                roles = [i for i in vanitylogs.user.roles if not i.is_assignable()]
                                return await vanitylogs.user.edit(roles=roles, reason=vanityreason)
                            else:
                                return
                        except Exception as e:
                            await vanitylogs.user.kick(reason="Could not strip roles, force kicked.")
                            return await guild.owner.send(embed=await AntinukeFailEmbed(member=f"{vanitylogs.user}", action="Changed guilds vanity URL", guild=str(guild.name), punishment=str(penalty), thumbnail=guild.icon))  
                    else:
                        return
                else:
                    return
            except:
                pass
            try:
                return
            except:
                return



    @commands.hybrid_group(
        aliases = ["an","anti"],
        usage = 'guild_owner',
        description = 'Server protection. Custom limits, templates, backups, custom penalties, and so much more!',
        brief = 'subcommand',
        help = '```Syntax: antinuke <subcommand>\nExample: antinuke penalty ban```'
        )
    async def antinuke(self, ctx): 
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Command: antinuke", description="24/7 Module to protect your server from attempted nukes.\n```Syntax: antinuke [subcommand] <argument>\nExample: antinuke penalty strip-roles```", color = discord.Color.blurple())
                embed.set_author(name="Antinuke help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('antinuke').walk_commands()])} ・ Antinuke")
                return await ctx.send(embed=embed)
        except Exception as e:
            print(e)

    @antinuke.group(
        usage = 'Guild owner',
        description = 'Create a antinuke backup to share, re-use or save',
        brief = 'None',
        help = '```Example: /backup create```'
    )
    async def backup(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="Group Command: antinuke backup", description="Settings to restore, create, view and share your antinuke settings!\n```Syntax: antinuke backup [subcommand]\nExample: antinuke backup create```", color = discord.Color.blurple())
            embed.set_author(name="antinuke backup help", icon_url=ctx.me.avatar.url)
            embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('antinuke').walk_commands()])} ・ antinuke backup")
            return await ctx.send(embed=embed)

    @backup.command(
        usage = 'Guild owner',
        description = 'Create a antinuke backup to share, re-use or save',
        brief = 'None',
        help = '```Example: /antinuke backup create```'
    )
    async def create(self, ctx):
        async with ctx.typing():
            if ctx.author.id == ctx.guild.owner.id:
                check = await self.dbbackup.count_documents({ "guild_id": ctx.guild.id})
                if check > 2:
                    check2 = await self.dbbackup.find_one({ "guild_id": ctx.guild.id })
                    return await ctx.send(embed=discord.Embed(color=self.urgecolor,title=f"{self.urgentmoji} Backup Interval", description=f"""Code: **{check2['code']}** (``{check2['time']}``)\n\nType ``/antinuke backup list`` to get a detailed view of backups.""").add_field(name="Interval", value="1 day").add_field(name="Last Backup", value=str(discord.utils.format_dt(check2['time'], style='R'))))
                else:
                    data = await self.db2.find_one({"guild_id": ctx.guild.id})
                    if data:
                        # fetching current 
                        firstembed = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                        firstembed.description = f"<a:whiteloading:1006977730912464936> Caching guild **object** with {len([m for m in ctx.guild.members])} **members**"
                        msg = await ctx.send(embed=firstembed)
                        data0 = data['--dangerous_permission_add']
                        data1 = data['--create_roles']
                        data2 = data['--create_channels']
                        data3 = data['--delete_channels']
                        data4 = data['--delete_roles']
                        data5 = data['--ban_members']
                        data6 = data['--kick_members']
                        data7 = data['--add_bot']
                        data8 = data['--mention_everyone']
                        data9 = data['--create_webhooks']
                        data10 = data['--create_threads']
                        data11 = data['--change_guild_vanity']
                        data12 = data['--change_guild_icon']
                        data13 = data['--change_guild_verification']
                        data14 = data['--change_guild_name']
                        data15 = data['--change_guild_rules']
                        data16 = data['--change_guild_banner']
                        await asyncio.sleep(1.6)
                        secondembed = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                        secondembed.description = f"<:download:921754124477935616> **Antinuke settings inserted..** Fetching **limits**"
                        await msg.edit(embed=secondembed)
                        default_limit = await self.db.find_one({ "guild_id": ctx.guild.id })
                        get_limit = await self.limits.find_one({"guild_id": ctx.guild.id})
                        if not get_limit:
                            create_roles = default_limit['threshold']
                            delete_roles = default_limit['threshold']
                            create_channels = default_limit['threshold']
                            delete_channels = default_limit['threshold']
                            delete_stickers= default_limit['threshold']
                            delete_emojis = default_limit['threshold']
                            ban_members = default_limit['threshold']
                            kick_members = default_limit['threshold']
                            create_webhooks = default_limit['threshold']
                            mention_everyone = default_limit['threshold']
                        else:
                            create_roles = get_limit['--create_roles']
                            delete_roles = get_limit['--delete_roles']
                            create_channels = get_limit['--create_channels']
                            delete_channels = get_limit['--delete_channels']
                            delete_stickers= get_limit['--delete_stickers']
                            delete_emojis = get_limit['--delete_emojis']
                            ban_members = get_limit['--ban_members']
                            kick_members = get_limit['--kick_members']
                            create_webhooks = get_limit['--create_webhooks']
                            mention_everyone = get_limit['--mention_everyone']
                        whld = default_limit['whitelisted']
                        whitelisted = []
                        for i in whld:
                            whitelisted.append(i)
                        own = default_limit['owners']
                        owners = []
                        for i in own:
                            owners.append(i)
                        punishment = default_limit['punishment']
                        #time = default_limit['time']
                        await asyncio.sleep(1)
                        thirdembed = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                        thirdembed.description = f"<:check:921544057312915498> **Collected** now **inserting guild** ``{ctx.guild.id}`` with a **whitelist** of **{len(whitelisted)} members**, **{len(owners)} antinuke admins**, and **punishment** set to **{punishment}**."
                        await msg.edit(embed=thirdembed)

                        ########################################################################
                        time = datetime.datetime.now()
                        try:
                            code = await codeGen()
                            await self.db2backup.insert_one({
                                'guild_id': ctx.guild.id,
                                'creator': ctx.author.id,
                                'time': time,
                                'code': str(code),
                                '--create_roles': data1,
                                '--delete_roles': data4,
                                '--create_channels': data2,
                                '--delete_channels': data3,
                                '--dangerous_permission_add': data0,
                                '--ban_members': data5,
                                '--kick_members': data6,
                                '--create_webhooks': data9,
                                '--add_bot': data7,
                                '--change_guild_vanity': data11,
                                '--change_guild_icon': data12,
                                '--change_guild_verification': data13,
                                '--change_guild_name': data14,
                                '--change_guild_rules': data15,
                                '--change_guild_banner': data16,
                                '--create_threads': data10,
                                '--mention_everyone':data8,
                            })

                            await self.limitsbackup.insert_one({
                                'guild_id': ctx.guild.id,
                                'code': str(code),
                                'time': time,
                                'creator': ctx.author.id,
                                '--create_roles': create_roles,
                                '--delete_roles': delete_roles,
                                '--create_channels': create_channels,
                                '--delete_channels': delete_channels,
                                '--delete_stickers': delete_stickers,
                                '--delete_emojis': delete_emojis,
                                '--ban_members': ban_members,
                                '--kick_members': kick_members,
                                '--create_webhooks': create_webhooks,
                                '--mention_everyone': mention_everyone
                            })

                            await self.dbbackup.insert_one({
                                'guild_id': ctx.guild.id,
                                'time': time,
                                'code': str(code),
                                'creator': ctx.author.id,
                                'owners': owners,
                                'whitelisted': whitelisted,
                                'punishment': punishment,
                                'threshold': 2
                            })
                            await asyncio.sleep(0.5)
                            lastembed = discord.Embed(color=0x43B581)
                            lastembed.set_author(name="Success", icon_url="https://cdn.discordapp.com/emojis/921544057312915498.webp?size=44&quality=lossless")
                            lastembed.description = f"Successfully **created antinuke backup** with the **code**: **{code}**\n**Contains:**\n**17** triggers **|** **{len(whitelisted)}** members **whitelisted**\n**{len(owners)}** antinuke **admins** **|** **17** limits\nPunishment: saved as set to **{punishment}**\n\n**Usage**:\n```/backup load [backup_code]: {code}``````/backup search [backup_code]: {code}```"
                            lastembed.set_footer(text='Need help? Visit the support server @ https://blame.gg/discord')
                            await msg.edit(embed=lastembed)
                        except Exception as e:
                            print(e)
            else:
                return await util.send_error(ctx, "Only the ``guild_owner`` has access to this command.")
                #inserted Settings
    @backup.command(
        aliases = ['find', 'lookup', 'index', 'info'],
        usage = 'send_messages',
        description = 'Get in depth details about an antinuke backup code!',
        brief = 'code',
        help = '```Syntax: /antinuke backup search [code]\nExample: /antinuke backup search BSGVQG4G```'
    )
    async def search(self, ctx, code: str):
        async with ctx.typing():
            check = await self.dbbackup.find_one({"code": code})
            if check:
                em1 = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                em1.description = f"<:check:921544057312915498> **Found code:** Please wait while I fetch its **settings**"
                msg = await ctx.send(embed=em1)
                code = check['code']
                creator = check['creator']
                whld = check['whitelisted']
                whitelisted = []
                for i in whld:
                    whitelisted.append(i)
                own = check['owners']
                owners = []
                for i in own:
                    owners.append(i)
                punishment = check['punishment']
                backup_threshold = check['threshold']
            #########################################################
                data = await self.db2backup.find_one({'code': code})
                data0 = data['--dangerous_permission_add']
                data1 = data['--create_roles']
                data2 = data['--create_channels']
                data3 = data['--delete_channels']
                data4 = data['--delete_roles']
                data5 = data['--ban_members']
                data6 = data['--kick_members']
                data7 = data['--add_bot']
                data8 = data['--mention_everyone']
                data9 = data['--create_webhooks']
                data10 = data['--create_threads']
                data11 = data['--change_guild_vanity']
                data12 = data['--change_guild_icon']
                data13 = data['--change_guild_verification']
                data14 = data['--change_guild_name']
                data15 = data['--change_guild_rules']
                data16 = data['--change_guild_banner']
            #############################################
                get_limit = await self.limitsbackup.find_one({"code": code})
                create_roles = get_limit['--create_roles']
                delete_roles = get_limit['--delete_roles']
                create_channels = get_limit['--create_channels']
                delete_channels = get_limit['--delete_channels']
                delete_stickers= get_limit['--delete_stickers']
                delete_emojis = get_limit['--delete_emojis']
                ban_members = get_limit['--ban_members']
                kick_members = get_limit['--kick_members']
                create_webhooks = get_limit['--create_webhooks']
                mention_everyone = get_limit['--mention_everyone']
                await asyncio.sleep(2)
                em2 = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                get_creator = self.bot.get_user(creator)
                #em2.title = f"<:check:921544057312915498> Code: {code}"
                #em2.add_field(name="Creator", value=f"```{get_creator}```", inline=False)
                #em2.add_field(name="Penalty", value=f"```{punishment}```", inline=False)
                em2.add_field(name=f"Whitelist ({len(whitelisted)})", value=f"```ruby\n{whitelisted}\n```", inline=True)
                em2.add_field(name=f"Admins ({len(owners)})", value=f"```ruby\n{owners}\n```", inline=True)
                em2.set_footer(text=f"{code} created by: {get_creator} | Punishment: {punishment}", icon_url=ctx.guild.icon.url)
                bracket = "{"
                endbracket = "}"
                formats = "``{trigger: [status, limit]}``"
                em2.set_author(name=f"Settings for code: {code}", icon_url=ctx.guild.icon.url)
                em2.add_field(name="Internal Settings", value=f"\n**Format:** {formats}\n```ruby\n📁 {code}:\n{bracket}dangerous_perms: [{data0}, N/A], create_roles: [{data1}, {create_roles}], create_channels: [{data2}, {create_channels}], delete_channels: [{data3}, {delete_channels}], delete_roles: [{data4}, {delete_roles}], ban_members: [{data5}, {ban_members}], kick_members: [{data6}, {kick_members}], add_bot: [{data7}, N/A], mention_everyone: [{data8}, {mention_everyone}], create_webhooks: [{data9}, {create_webhooks}], create_threads: [{data10}, N/A], change_vanity: [{data11} N/A], change_icon: [{data12}, N/A], change_verification: [{data13}, N/A], change_name: [{data14}, N/A], change_rules: [{data15}, N/A], change_banner: [{data16}, N/A]{endbracket}\n```", inline=False)
                await msg.edit(embed=em2)
            else:
                em1 = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                em1.description = f"{self.xmoji} {ctx.author.mention}: **Code: {code}** was **not found**"
                msg = await ctx.send(embed=em1)
    
    @backup.command(
        aliases = ['list', 'all'],
        usage = 'send_messages',
        description = "View all the antinuke backups you've created over time!",
        brief = 'page',
        help = '```Example: /antinuke backup list```'
    )
    async def view(self, ctx, page=None):
        if page:
            page=None
        check = await self.dbbackup.find_one({'creator': ctx.author.id})
        if check:
            #{discord.utils.format_dt(datetime.now(), style='R')}
            check_existing = self.dbbackup.find({"creator": ctx.author.id})
            triggers = []
            responses = []
            times = []
            for trigger in await check_existing.to_list(length=50):
                trigs = trigger['code']
                resps = trigger['time']
                auths = trigger['guild_id']
                triggers.append(trigs)
                times.append(resps)
                responses.append(auths)
            for i in times:
                i = discord.utils.format_dt(i, style='R')
            for bo in responses:
                bo = self.bot.get_guild(bo)
            responseStr = [f"**{triggers}**\n{bo} - {i}" for triggers in zip(triggers)]
            rows = []
            content = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
            content.title = "Your Backup's"
            content.description = ""
            content.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

            for count, d in enumerate(responseStr, start=1):
                rows.append(f"{d}")
            content.set_footer(text=f"Displaying (1 - {count}) of {count} backups")
            await util.send_as_pages(ctx, content, rows)
        else:
            em1 = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
            em1.description = f"{self.xmoji} {ctx.author.mention}: **You have 0 antinuke backups.**"
            msg = await ctx.send(embed=em1)


    @commands.command(aliases = ['format'])
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx, *, params):
        #'''Send complex rich embeds with this command!
        #```
        #{description: Discord format supported}
        #{title: required | url: optional}
        #{author: required | icon: optional | url: optional}
        #{image: image_url_here}
        #{thumbnail: image_url_here}
        #{field: required | value: required}
        #{footer: footer_text_here | icon: optional}
        #{timestamp} <-this will include a timestamp
        #```
        #'''
        user = ctx.author
        if params.startswith('(embed)'):
            params = params.replace('(embed)', '')
            params = await util.test_vars(ctx, user, params)
            if "content:" in params.lower():
                em = await util.to_embed(ctx, params)
                msg = await util.to_content(ctx, params)
                try:
                    #await ctx.send(msg)
                    await ctx.send(content=msg,embed=em)
                except Exception as e:
                    await ctx.send(f"```{e}```")
            else:
                em = await util.to_embed(ctx, params)
                try:
                    #await ctx.send(msg)
                    await ctx.send(embed=em)
                except Exception as e:
                    await ctx.send(f"```{e}```")
        else:
            return await ctx.send('Must begin with ``(embed)``')

        #embed = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))

#END OF GROUPING COMMAND
    @commands.command()
    async def sync(self, ctx):
        if ctx.author.id in developers:
            await self.bot.tree.sync()
            await ctx.send("successfully synced all guilds")
        else:
            return
        
    @antinuke.command(
        aliases = ['log', 'logger', 'logging'],
        usage = "Guild owner",
        description = "Setup whether you  want to have antinuke logs set in a channel or DMs",
        brief = "None",
        help = "```Syntax: antinuke logs [channel or 'dms']\nExample: antinuke logs dms```"
    )
    async def logs(self, ctx, type):
        channels = ['dms', 'Dms', 'Dm', 'dm']
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers:
            check = await self.logs.find_one({ "guild_id": ctx.guild.id })
            if not check:
                if type in channels:
                    channel2 = self.bot.get_user(ctx.author.id)
                    await self.logs.insert_one({
                        "guild_id": ctx.guild.id,
                        "channel": ctx.author.id
                    })
                    return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} **Antinuke Logging** will now be sent to you **via DM's**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                if type not in channels:
                    try:
                        channel2 = self.bot.get_channel(int(type))
                    except ValueError:
                            return await util.send_error(ctx, "Channel not found")
                    if channel2:
                        await self.logs.insert_one({
                        "guild_id": ctx.guild.id,
                        "channel": int(type)
                    })
                        return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} **Antinuke Logging** will now be sent in {channel2.mention}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                    else:
                        return await util.send_error(ctx, f"Type: **{type}** not supported.")
            else:
                return await util.send_error(ctx, f"Logging is already set to channel")
        else:
            return await util.send_error(ctx, "Only ``antinuke admins`` have access to this command.")
                
    @antinuke.command(
        aliases = ['rlog', 'clearlogs', 'removelog', 'clearlog'],
        usage = "Guild owner",
        description = "Setup whether you  want to have antinuke logs set in a channel or DMs",
        brief = "None",
        help = "```Syntax: antinuke logs [channel or 'dms']\nExample: antinuke logs dms```"
    )
    async def removelogs(self, ctx):
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers:
            check = await self.logs.find_one({ "guild_id": ctx.guild.id })
            if check:
                await self.logs.delete_one({"guild_id": ctx.guild.id})
                return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} **Antinuke Logging** has been **disabled**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
            else:
                return await util.send_error(ctx, f"Logging has not been setup")
        else:
            return await util.send_error(ctx, "Only ``antinuke admins`` have access to this command.")


    @antinuke.command(
        usage = 'Guild owner',
        description = "Builds the limits for the guild",
        brief = "None",
        help = "```Example: antinuke limitsetup```"
    )
    async def limitsetup(self, ctx):
        try:
            dataa = await self.db.find_one({ "guild_id": ctx.guild.id })
            checker = dataa['owners']
            if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers or ctx.author.id in checker:
                data = await self.db.find_one({ "guild_id": ctx.guild.id })
                if not data:
                    return await util.send_error(ctx, "The ``antinuke`` is not enabled in this server.")
                if data:
                    find_limits = await self.limits.find_one({ "guild_id": ctx.guild.id })
                    if find_limits:
                        return await util.send_blurple(ctx,"They're already setup use ``help antinuke limit`` to change them.")
                    else:
                        await self.limits.insert_one({
                            "guild_id": ctx.guild.id,
                            "--create_roles": 2,
                            "--delete_roles": 2,
                            "--create_channels": 2,
                            "--delete_channels": 2,
                            "--delete_stickers": 2,
                            "--delete_emojis": 2, 
                            "--ban_members": 2, 
                            "--kick_members": 2,
                            "--create_webhooks": 2,
                            "--mention_everyone": 2
                        })
                        await util.send_blurple(ctx, f'The antinuke limits have now been set to a default of ``2 per 30s``. You can change this with: ``{ctx.prefix}help antinuke limit``')
                        self.cacheThresholds.restart()
            else:
                return await util.send_error(ctx, "Only ``antinuke admins`` have access to this command.")
        except Exception as e:
                await util.send_issue(ctx, "The ``antinuke`` is not enabled in this server.")
                return print(e) #logging errors


    @antinuke.command(
        aliases = ['threshold', 'count'],
        usage = 'Guild owner',
        description = 'Set an antinuke limit on a flag that your staff cannot pass or else will be punished',
        brief = "flag, int",
        help = "```Syntax: antinuke limit [flag] <int>\nExample: antinuke limit --create_roles 5```"
    )
    async def limit(self, ctx, flag=None, limit:int=None):
        flags=["--create_roles","--delete_roles","--create_channels","--delete_channels","--delete_stickers","--delete_emojis","--ban_members","--kick_members","--create_webhooks","--mention_everyone"]
        try:
            if limit == None:
                limit =2
            dataa = await self.db.find_one({ "guild_id": ctx.guild.id })
            checker = dataa['owners']
            if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers or ctx.author.id in checker:
                data = await self.db.find_one({ "guild_id": ctx.guild.id })
                if not data:
                    return await util.send_issue(ctx, "The ``antinuke`` is not enabled in this server.")
                if flag == None:
                    return await util.send_issue(ctx, "Make sure to include the ``trigger`` yoou want to set a ``limit`` to.")
                if flag.lower() not in flags:
                    flagged="\n".join(flag for flag in flags)
                    return await ctx.send(embed=discord.Embed(title=f"{self.urgentmoji} Supported Limits", description=f"That flag is not supported with a limit. Here are the supported limit flags:\n```{flagged}```", color=self.urgecolor))
                if limit > 10:
                    return await util.send_error(ctx, "The limit cannot be greater than ``10``")
                else:
                    try:
                        await self.limits.update_one({ "guild_id": ctx.guild.id }, { "$set": { f"{flag.lower()}": limit}})
                        await util.send_blurple(ctx, f"The trigger ``{flag.lower()}`` limit has been set to ``{limit} per 30s``")
                        return self.cacheThresholds.restart()
                    except:
                        pass
                        return await util.send_blurple(ctx, f"Use ``antinuke limitsetup`` first, then use this command. Sorry for the inconvenience.")
            else:
                return await util.send_error(ctx, "Only ``antinuke admins`` have access to this command.")
        except Exception as e:
                await util.send_issue(ctx, "The ``antinuke`` is not enabled in this server.")
                return print(e) #logging errors





#START ENABLE AND DISABLEMENT OF ANTINUKE

    @antinuke.command(
        aliases=["enable"],
        usage = "Guild owner",
        description = "Toggles the antinukes status to enabled.",
        brief = "None",
        help = f"```Example: antinuke enable```"
        )
    async def on(self, ctx):
        async with ctx.typing():
            try:
                if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers: #sorrows ID for full control over antinuke
                    check = await self.db.count_documents({ "guild_id": ctx.guild.id })
                    if check: # Mean's the antinuke is already enabled
                        data = await self.db.find_one({"guild_id": ctx.guild.id})
                        when = data["time"]
                        vanity = data['vanity']
                        return await util.send_issue(ctx, 'The ``antinuke`` is already enabled in this server!')
                    else: # if not, then we create insert document(s) for it
                        await util.send_blurple(ctx, f"The ``antinuke`` is now enabled. You can ``set`` limits on certain events with ``{ctx.prefix}antinuke limit``. You can also begin whitelisting staff you trust so the antinuke doesn't ``penalize`` them.")
                        await self.db.insert_one({
                            "whitelisted": [776128410547126322, ctx.guild.owner.id],
                            "owners": [776128410547126322, ctx.guild.owner.id],
                            "time": str(d2),
                            "vanity": None,
                            "punishment": "ban",
                            "threshold": 2,
                            "guild_id": ctx.guild.id
                        })
                        await self.db2.insert_one({ #all of our settings
                            "guild_id": ctx.guild.id,
                            "--dangerous_permission_add": 'Enabled',
                            "--create_roles": 'Enabled',
                            "--create_channels": 'Enabled',
                            "--delete_channels": 'Enabled',
                            "--update_channels": 'Enabled',
                            "--update_roles": 'Enabled',
                            "--delete_roles": 'Enabled',
                            "--ban_members": 'Enabled',
                            "--kick_members": 'Enabled',
                            "--add_bot": 'Enabled',
                            "--mention_everyone": 'Enabled',
                            "--create_webhooks": 'Enabled',
                            "--create_threads": 'Enabled', 
                            "--change_guild_vanity": 'Enabled',
                            "--change_guild_icon": "Enabled", 
                            "--change_guild_verification": "Enabled", 
                            "--change_guild_name": 'Enabled',
                            "--change_guild_rules": 'Enabled',
                            "--change_guild_banner": 'Enabled',
                            "--delete_emojis": 'Enabled',
                            "--delete_stickers": 'Enabled'
                        })
                        try:
                            await asyncio.sleep(1)
                            theinv = await ctx.guild.vanity_invite()
                            await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "vanity": (str(theinv)[19:45])}})
                        except Exception as e:
                            print(e)
                        #today = date.today()
                        #d2 = today.strftime("%B %d, %Y") #month, day, year
                        #await self.db.update_one({"guild_id": ctx.guild.id}, {"$set": {"time": str(d2)}}) #inserting the date the module was enabled
                        await self.limits.insert_one({
                            "guild_id": ctx.guild.id,
                            "--create_roles": 2,
                            "--delete_roles": 2,
                            "--create_channels": 2,
                            "--delete_channels": 2,
                            "--delete_stickers": 2,
                            "--delete_emojis": 2, 
                            "--ban_members": 2, 
                            "--kick_members": 2,
                            "--create_webhooks": 2,
                            "--mention_everyone": 2
                        })
                        self.cacheThresholds.restart()
                        self.cacheSettings.restart()
                        self.cachePunishments.restart()
                else:
                    return await util.send_issue(ctx, 'Only the ``server owner`` has access to this command.')
            except Exception as e:
                return print(e)

    @antinuke.command(
        aliases = ['disable'],
        usage = "Guild owner",
        description = "Toggles the antinukes status to disabled",
        brief = "None",
        help = "```Example: antinuke disable```")
    async def off(self, ctx):
        try:
            if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers:
                check = await self.db.count_documents({ "guild_id": ctx.guild.id })
                if not check:
                    await util.send_error(ctx, "The ``antinuke`` is not enabled in this server.")
                else:
                    await util.send_blurple(ctx, "The antinuke has been ``disabled``.")
                    await self.db2.delete_one({ "guild_id": ctx.guild.id }), await self.db.delete_one({ "guild_id": ctx.guild.id }), await self.limits.delete_one({ "guild_id": ctx.guild.id })
                    self.cacheThresholds.restart()
                    self.cacheSettings.restart()
                    self.cachePunishments.restart()
            else:
                return await util.send_issue(ctx, 'Only the ``server owner`` has access to this command.')
        except Exception as e:
            print(e)


#END ENABLE AND DISABLEMENT OF ANTINUKE


    @antinuke.command(
        usage = "Guild owner",
        description = "Give a member permission to edit the antinuke's settings, like the guild owner.",
        brief = "user",
        help = "```Syntax: antinuke admin [user]\nExample: antinuke admin @jacob```"
    )
    async def admin(self, ctx, user: discord.User):
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers:
            try:
                data = await self.db.find_one({ "guild_id": ctx.guild.id })
                yuh = data["owners"]

                if not data:
                    return await util.send_error(ctx, "The ``antinuke`` is not enabled in this server.")
                elif user.id in yuh: 
                    await util.send_blurple(ctx, f"<@{user.id}> is no longer an ``antinuke admin``.")
                    return await self.db.update_one({ "guild_id": ctx.guild.id }, { "$pull": { "owners": user.id}}) 
                elif len(yuh) > 15:
                    return await util.send_issue(ctx, "You cannot have more than ``15`` antinuke admins per guild.")
                else:
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$push": { "owners": user.id}}) 
                    self.cachePunishments.restart()
                    return await util.send_blurple(ctx, f"``{user.id}`` <@{user.id}> is now an ``antinuke admin``. They now have permission to edit the ``antinukes settings``.")

            except Exception as e:
                return await util.send_issue(ctx, "The ``antinuke`` is not enabled in this server.") #logging errors
        else:
            return await util.send_error(ctx, "Only ``antinuke admins`` have access to this command.") #access denied


    @antinuke.command(
        usage = "Guild owner",
        description = "View the antinuke admins in the server",
        brief = "None",
        help = "```Example: antinuke admins```"
    )
    async def admins(self, ctx):
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers:
            try:
                meow = await self.db.find_one({ "guild_id": ctx.guild.id })
                data = meow['owners']
                content = discord.Embed(description="", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                content.set_author(name=f"Antinuke admins in {ctx.guild.name}", icon_url=ctx.guild.icon.url)

                new = []
                rows = []
                for i in data:
                    msg = self.bot.get_user(i)
                    if msg.bot and not msg.public_flags.verified_bot:
                        new.append(f"**{msg}** - <@{i}> <:bot:921595812956479499>")
                    if msg.public_flags.verified_bot:
                        new.append(f"**{msg}** - <@{i}> <:blurple_bot2:921812004715524157><:blurple_bot1:921812007798337546>")
                    if msg.id ==ctx.guild.owner.id:
                        new.append(f"**{msg}** - <@{i}> <:CrownGold:1003370254447157328>")
                    if not msg.bot and not msg.id == ctx.guild.owner.id:
                        new.append(f"**{msg}** - <@{i}> <a:8263blurplemembers:921796523182919780>")
                for count, a in enumerate(new, start=1):
                    rows.append(f"``{count}.)`` {a}")
                content.set_footer(text=f"Antinuke admins: ({len(new)}/15) Entries", icon_url=ctx.guild.icon.url)
                await util.send_as_pages(ctx, content, rows)


            except Exception as e:
                return await util.send_issue(ctx, "The ``antinuke`` is not enabled in this server.") 
        else:
            await util.send_error(ctx, f"Only ``antinuke admins`` have access to this command.")


# WHITELISTING | # WHITELISTING# WHITELISTING | # WHITELISTING# WHITELISTING | # WHITELISTING


    @antinuke.command(
        aliases = ['whl', 'whit', 'wl'],
        usage = "Guild owner, Administrator",
        description = "Exempts a user from being affected by the antinuke until they are unwhitelisted",
        brief = "User, Member",
        help = "```Syntax: antinuke whitelist [user]\nExample: antinuke whitelist @jacob```"
        )
    @commands.has_permissions(administrator=True)
    async def whitelist(self, ctx, user: discord.User=None):
        try:
            dataa = await self.db.find_one({ "guild_id": ctx.guild.id })
            checker = dataa['owners']
            if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers or ctx.author.id in checker:
                check = await self.db.count_documents({ "guild_id": ctx.guild.id })
                data = await self.db.find_one({ "guild_id": ctx.guild.id })
                yuh = data["whitelisted"]

                if not check: #If the guild ID was not found, the antinuke is not enabled
                    return await util.send_error(ctx, "The ``antinuke`` is not enabled in this server")
                elif user.id in yuh: #Checks if the user's id is already whitelisted
                    return await util.send_error(ctx, f"``{user.id}`` <@{user.id}> is already in this guild's whitelist.")
                else:
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$push": { "whitelisted": user.id}}) #guild id found in db. therefore, pushing the users id into "whitelisted"
                    self.cachePunishments.restart()
                    return await util.send_blurple(ctx, f"``{user.id}`` <@{user.id}> is now whitelisted in this server.")
            else:
                return await util.send_issue(ctx, "Only ``antinuke admins`` have access to this command.") #access denied
        except Exception as e:
                await util.send_error(ctx, "The ``antinuke`` is not enabled in this server.")
                return print(e) #logging errors

    @antinuke.command(
        aliases = ['unwl', 'uwl', 'unwhl', 'uwhl'],
        usage = "Guild owner, Administrator",
        description = "Removes a user from the whitelist leaving them vulnerable to the antinukes triggers",
        brief = "User, Member",
        help = "```Syntax: antinuke unwhitelist [user]\nExample: antinuke unwhitelist @jacob```"
    )
    async def unwhitelist(self, ctx, user: discord.User=None):
        try:
            dataa = await self.db.find_one({ "guild_id": ctx.guild.id })
            checker = dataa['owners']
            if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers or ctx.author.id in checker:
                check = await self.db.count_documents({ "guild_id": ctx.guild.id })
                data = await self.db.find_one({ "guild_id": ctx.guild.id })
                yuh = data["whitelisted"]
                peep = data['owners']
                if not check:
                    return await util.send_error(ctx, "The ``antinuke`` is not enabled in this server")
                elif user==None:
                    return await util.send_issue(ctx, "Please provide a user to whitelist.")
                elif user.id not in yuh:
                    return await util.send_issue(ctx, f"``{user.id}`` is not in this server's ``whitelist``.")
                else:
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$pull": { "whitelisted": user.id }})
                    self.cachePunishments.restart()
                    return await util.send_blurple(ctx, f"``{user.id}`` <@{user.id}> has been removed from the ``whitelist``.")
            else:
                await util.send_issue(ctx, "Only ``antinuke admins`` have access to this command.")
        except Exception as e:
            await util.send_error(ctx, "The ``antinuke`` is not enabled in this server.")
            return print(e)

    @antinuke.command(
        usage = "Guild owner, Administrator",
        description = "View's the current antinuke whitelist",
        brief = "None",
        help = "```Example: antinuke whitelisted```"
    )
    async def whitelisted(self, ctx):
        try:
            dataa = await self.db.find_one({ "guild_id": ctx.guild.id })
            checker = dataa['owners']
            if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers or ctx.author.id in checker:
                check = await self.db.find_one({ "guild_id": ctx.guild.id })
                if not check:
                    return await util.send_error(ctx, f'The antinuke module is not enabled. Therefore, there are no whitelisted users.')
                else:
                    data = await self.db.find_one({ "guild_id": ctx.guild.id })
                    whitelist = data["whitelisted"]
                    content = discord.Embed(description="", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                    content.set_author(name=f"Whitelisted users in {ctx.guild.name}", icon_url=ctx.author.display_avatar.url)
                    new = []
                    rows = []
                    for i in whitelist:
                        msg = self.bot.get_user(i)
                        if msg is None:
                            continue
                        if msg.bot and not msg.public_flags.verified_bot:
                           new.append(f"**{msg}** - <@{i}> <:bot:921595812956479499>")
                        if msg.public_flags.verified_bot:
                            new.append(f"**{msg}** - <@{i}> <:blurple_bot2:921812004715524157><:blurple_bot1:921812007798337546>")
                        if msg.id ==ctx.guild.owner.id:
                            new.append(f"**{msg}** - <@{i}> <:CrownGold:1003370254447157328>")
                        if not msg.id == ctx.guild.owner.id and not msg.public_flags.verified_bot and not msg.bot:
                            new.append(f"**{msg}** - <@{i}> <a:8263blurplemembers:921796523182919780>")
                    for count, a in enumerate(new, start=1):
                        rows.append(f"``{count}.)`` {a}")
                    content.set_footer(text=f"Whitelisted: ({len(new)}) Entries", icon_url=ctx.guild.icon.url)
                    await util.send_as_pages(ctx, content, rows)

            else:
                return await util.send_issue(ctx, "Only ``antinuke admins`` have access to this command.")
        except Exception as e:
            await util.send_error(ctx, "The ``antinuke`` is not enabled in this server.")
            return print(e)


# END OF WHITELISTING | # END OF WHITELISTING # END OF WHITELISTING | # END OF WHITELISTING






#START SETUP OF ANTINUKE


    @antinuke.command()
    async def setup(self, ctx):
        #embed = discord.Embed(description='**Asura Antinuke**\n\n ;antinuke setup - ``How to settup the antinuke``\n ;antinuke enable - ``Activate the antinukes settings``\n ;antinuke disable - ``Deactivate the antinukes settings``\n ;antinuke config - ``View the antinukes current settings``\n;antinuke whitelist - ``Whitelist a user from being affected by the antinuke``\n;antinuke unwhitelist - ``Remove a user from the whitelist``\n;antinuke whitelisted - ``View all users that are on the whitelist``\n;antinuke penalty - ``Set the antinukes penalty``\n;antinuke off - ``Turns off the antinuke``\n;antinuke on - ``Turns on the antinuke``', color=0x006eff)
        #embed.add_field(name='Security', value=f'**`setup`, `toggle`, `settings`, `whitelist`, `punishment`, `whitelisted`, `unwhitelist`**', inline=False)
        embed = discord.Embed(title='<:BadgeCertifiedMod:925643690750382121> How to setup the Antinuke', color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
        embed.add_field(name='__What does the Antinuke do?__', value=f'\n<a:info:921613282199089172> Blames antinuke will detect any suspicous behaviour (trggers/events) which may result in an attempted nuke. You can view and toggle these specific features to your liking!', inline=False)
        embed.add_field(name='How to set it up', value="> <:B_number_1:929872701651316806> We want to enable the antinuke by running the ``;antinuke enable`` command. You'll then be approached with some steps you may want to follow.\n> <:B_number_2:929872731812560946> View the antinukes current settings with ``;antinuke settings``; you can toggle these to your preferances at any point, if you're the guild owner.\n> <:B_number_3:929872751722913862> Whitelisting: You may want to ``whitelist`` any of your admins/staff you trust, so they won't be affected\n\n> <:a_box_check:929879789609812088> You did it! The antinuke should be properly set if all was followed. **To check everything is well, run the** ``antinuke debug`` **command** or join the support server http://blame.gg", inline=False)
        await ctx.channel.send(embed=embed)

#END SETUP OF ANTINUKE


    @antinuke.command(
        aliases = ['mode', 'template'],
        usage = "Guild owner, Administrator",
        description = "Set the antinukes settings to one of our **already made** templates",
        brief = "preset",
        help = "```Syntax: antinuke preset [preset]\nExample #1: antinuke preset low\nExample #2: antinuke preset medium\nExample #3: antinuke preset high\nExample #4: antinuke preset max```")
    async def preset(self, ctx, preset=None):
        lowPresetList = ["low", "1"]
        mediumPresetList = ["mid", 'medium', '2']
        highPresetList = ['high', '3', 'aids']
        hitmanPresetList = ['hitman', 'max', '4', 'cutthroat']
        try:
            check = await self.db.find_one({ "guild_id": ctx.guild.id })
            checkers = check['owners']
            if check:
                if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers or ctx.author.id in checkers:
                    try:
                        if preset == None:
                            return await util.send_error(ctx, "Please specify a preset, Our ``presets`` include, ``(LOW, MEDIUM, HIGH, HITMAN)``")
                        if preset.lower() in lowPresetList:
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--dangerous_permission_add": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--create_roles": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--create_channels": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--delete_channels": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--delete_roles": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--ban_members": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--kick_members": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--add_bot": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--update_roles": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--update_channels": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--delete_stickers": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--delete_emojis": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--mention_everyone": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--create_webhooks": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--create_threads": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_vanity": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_icon": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_verification": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_name": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_rules": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_banner": "Disabled"}})
                            await util.send_blurple(ctx, f"I've changed this servers ``antinuke settings`` to thos of the preset: ``{preset}``")
                            self.cacheSettings.restart()

                        elif preset.lower() in mediumPresetList:
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--dangerous_permission_add": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--create_roles": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--create_channels": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--delete_channels": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--delete_roles": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--ban_members": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--kick_members": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--add_bot": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--update_roles": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--update_channels": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--delete_stickers": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--delete_emojis": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--mention_everyone": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--create_webhooks": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--create_threads": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_vanity": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_icon": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_verification": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_name": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_rules": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_banner": "Disabled"}})
                            await util.send_blurple(ctx, f"I've changed this servers ``antinuke settings`` to thos of the preset: ``{preset}``")
                            self.cacheSettings.restart()

                        elif preset.lower() in highPresetList:
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--dangerous_permission_add": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--create_roles": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--create_channels": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--delete_channels": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--delete_roles": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--ban_members": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--kick_members": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--add_bot": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--update_roles": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--update_channels": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--delete_stickers": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--delete_emojis": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--mention_everyone": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--create_webhooks": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--create_threads": "Disabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_vanity": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_icon": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_verification": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_name": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_rules": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_banner": "Enabled"}})
                            await util.send_blurple(ctx, f"I've changed this servers ``antinuke settings`` to thos of the preset: ``{preset}``")
                            self.cacheSettings.restart()

                        elif preset.lower() in hitmanPresetList:
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--dangerous_permission_add": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--create_roles": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--create_channels": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--delete_channels": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--delete_roles": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--ban_members": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--kick_members": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--add_bot": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--update_roles": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--update_channels": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--delete_stickers": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--delete_emojis": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--mention_everyone": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--create_webhooks": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--create_threads": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_vanity": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_icon": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_verification": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_name": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_rules": "Enabled"}})
                            await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { "--change_guild_banner": "Enabled"}})
                            await util.send_blurple(ctx, f"I've changed this servers ``antinuke settings`` to thos of the preset: ``{preset}``")
                            self.cacheSettings.restart()
                        else:
                            return await util.send_error(ctx, "That preset does not exist.")
                    except Exception as e:
                        print(e)
                else:
                    return await util.send_issue(ctx, "Only ``antinuke admins`` have access to this command.")
            else:
                return await util.send_error(ctx, "The ``antinuke``  is not enabled in this server.")
        except Exception as e:
            print(e)
 
#START TOGGLE EVENTS

    @antinuke.command(
        usage = "Guild owner, Administrator",
        description = "Toggle a certain antinuke trigger, on or off",
        brief = "trigger, bool",
        help = "```Syntax: antinuke toggle [trigger] <bool>\nExample #1: antinuke toggle --dangerous_permission_add off\nExample #2: antinuke toggle --create_channels on```"
    )
    async def toggle(self, ctx, flag=None, state:bool=False):
        flags=["--create_roles","--delete_roles","--update_roles","--create_channels","--delete_channels","--update_channels","--delete_stickers","--delete_emojis","--dangerous_permission_add","--ban_members","--kick_members","--create_webhooks","--add_bot","--change_guild_vanity","--change_guild_icon","--change_guild_verification","--change_guild_name","--change_guild_rules","--change_guild_banner","--create_threads","--mention_everyone"]
        try:
            if flag != None:
                if flag.lower() not in flags:
                    flagged="\n".join(flag for flag in flags)
                    return await ctx.send(embed=discord.Embed(color=self.urgecolor,title=f"{self.urgentmoji} Trigger required", description=f"""Toggle a specific antinuke trigger.\n```Syntax: ;antinuke toggle [trigger]\nExample: ;antinuke toggle --ban_members```\n**Need more?**\n<:invis:934961955855269889><:ARROW:934962001216696380> Only the server owner has access to the antinuke module and it's commands. If there are any issues you can contact us devs in the support server [here](https://discord.gg/blame)\n<:invis:934961955855269889><:ARROW:934962001216696380> Bug found? Report it in blames support server for some perks using the ``;invite`` command!\n\n**All antinuke triggers:**```{flagged}```"""))
            else:
                flagged="\n".join(flag for flag in flags)
                return await ctx.send(embed=discord.Embed(color=self.urgecolor,title=f"{self.urgentmoji} Trigger required", description=f"""Toggle a specific antinuke trigger.\n```Syntax: ;antinuke toggle [trigger]\nExample: ;antinuke toggle --ban_members```\n**Need more?**\n<:invis:934961955855269889><:ARROW:934962001216696380> Only the server owner has access to the antinuke module and it's commands. If there are any issues you can contact us devs in the support server [here](https://discord.gg/blame)\n<:invis:934961955855269889><:ARROW:934962001216696380> Bug found? Report it in blames support server for some perks using the ``;invite`` command!\n\n**All antinuke triggers:**```{flagged}```"""))
            check = await self.db.find_one({ "guild_id": ctx.guild.id })
            checker = check['owners']
            if check:
                if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers or ctx.author.id in checker:
                    try:
                        if state == True:
                            status="Enabled"
                        else:
                            status="Disabled"
                        await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { f"{flag.lower()}": f"{status}"}})
                        self.cacheSettings.restart()
                        return await util.send_blurple(ctx, f"The trigger: `{flag.lower()}` is now  `{status.lower()}` in this server.")
                    except Exception as e:
                        print(e)
                else:
                    return await util.send_issue(ctx, "Only ``antinuke admins`` have access to this command.")
            else:
                return await util.send_error(ctx, 'The ``antinuke`` is not enabled in this server.')
                await ctx.send(embed=embed6)       
        except Exception as e:
            print(e)


#END OF TOGGLE EVENTS




#START OF ANTINUKE DEBUG, STATUS

    @antinuke.command(
        aliases = ['settings', 'setting', 'stat'],
        usage = "Guild owner, Administrator",
        description = "View the current antinuke settings and their availability",
        brief = "None",
        help = "```Example: antinuke status```"
    )
    async def status(self, ctx):
        try:
            dataa = await self.db.find_one({ "guild_id": ctx.guild.id })
            checker = dataa['owners']
            penalty = dataa['punishment']
            if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers or ctx.author.id in checker:
                    data = await self.db2.find_one({ "guild_id": ctx.guild.id })
                    find = data['--dangerous_permission_add']
                    data1 = data['--create_roles']
                    #data17=data['--update_roles']
                    #data18=data['--update_channels']
                    #data19=data['--delete_stickers']
                    #data20=data['--delete_emojis']
                    data2 = data['--create_channels']
                    data3 = data['--delete_channels']
                    data4 = data['--delete_roles']
                    data5 = data['--ban_members']
                    data6 = data['--kick_members']
                    data7 = data['--add_bot']
                    data8 = data['--mention_everyone']
                    data9 = data['--create_webhooks']
                    data10 = data['--create_threads']
                    data11 = data['--change_guild_vanity']
                    data12 = data['--change_guild_icon']
                    data13 = data['--change_guild_verification']
                    data14 = data['--change_guild_name']
                    data15 = data['--change_guild_rules']
                    data16 = data['--change_guild_banner']

                    enabled_count = 0
                    disabled_count = 0

                    if "Enabled" in find:
                        enabled = "<:icons_Correct:921574654307610715>"
                        enabled_count += 1

                    else: 
                        enabled = "<:icons_Wrong:921574675639840838>"
                        disabled_count += 1 
                    #if "Enabled" in data17:
                        #enabled17 = "<:icons_Correct:921574654307610715>"
                        #enabled_count += 1

                    #else: 
                       # enabled17 = "<:icons_Wrong:921574675639840838>"
                      #  disabled_count += 1 
                    #if "Enabled" in data18:
                       # enabled18 = "<:icons_Correct:921574654307610715>"
                        #enabled_count += 1

                    #else: 
                        #enabled18 = "<:icons_Wrong:921574675639840838>"
                        #disabled_count += 1 
                    #if "Enabled" in data19:
                       # enabled19 = "<:icons_Correct:921574654307610715>"
                        #enabled_count += 1

                    #else: 
                        #enabled19 = "<:icons_Wrong:921574675639840838>"
                        #disabled_count += 1 
                    #if "Enabled" in data20:
                       # enabled20 = "<:icons_Correct:921574654307610715>"
                        #enabled_count += 1

                    #else: 
                        #enabled20 = "<:icons_Wrong:921574675639840838>"
                        #disabled_count += 1 


                    if "Enabled" in data1:
                        enabled1 = "<:icons_Correct:921574654307610715>"
                        enabled_count += 1
                        
                    else:
                        enabled1 = "<:icons_Wrong:921574675639840838>"
                        disabled_count += 1

                    if "Enabled" in data2:
                        enabled2 = "<:icons_Correct:921574654307610715>"
                        enabled_count += 1

                    else:
                        enabled2 = "<:icons_Wrong:921574675639840838>"
                        disabled_count += 1

                    if "Enabled" in data3:
                        enabled3 = "<:icons_Correct:921574654307610715>"
                        enabled_count += 1

                    else:
                        enabled3 = "<:icons_Wrong:921574675639840838>"
                        disabled_count += 1

                    if "Enabled" in data4:
                        enabled4 = "<:icons_Correct:921574654307610715>"
                        enabled_count += 1

                    else:
                        enabled4 = "<:icons_Wrong:921574675639840838>"
                        disabled_count += 1

                    if "Enabled" in data5:
                        enabled5 = "<:icons_Correct:921574654307610715>"
                        enabled_count += 1
                    else:
                        enabled5 = "<:icons_Wrong:921574675639840838>"
                        disabled_count += 1

                    if "Enabled" in data6:
                        enabled6 = "<:icons_Correct:921574654307610715>"
                        enabled_count += 1
                    else:
                        enabled6 = "<:icons_Wrong:921574675639840838>"
                        disabled_count += 1

                    if "Enabled" in data7:
                        enabled7 = "<:icons_Correct:921574654307610715>"
                        enabled_count += 1
                    else:
                        enabled7 = "<:icons_Wrong:921574675639840838>"
                        disabled_count += 1

                    if "Enabled" in data8:
                        enabled8 = "<:icons_Correct:921574654307610715>"
                        enabled_count += 1
                    else:
                        enabled8 = "<:icons_Wrong:921574675639840838>"
                        disabled_count += 1

                    if "Enabled" in data9:
                        enabled9 = "<:icons_Correct:921574654307610715>"
                        enabled_count += 1
                    else:
                        enabled9 = "<:icons_Wrong:921574675639840838>"
                        disabled_count += 1
                        
                    if "Enabled" in data10:
                        enabled10 = "<:icons_Correct:921574654307610715>"
                        enabled_count += 1
                    else:
                        enabled10 = "<:icons_Wrong:921574675639840838>"
                        disabled_count += 1

                    if "Enabled" in data11:
                        enabled11 = "<:icons_Correct:921574654307610715>"
                        enabled_count += 1
                    else:
                        enabled11 = "<:icons_Wrong:921574675639840838>"
                        disabled_count += 1

                    if "Enabled" in data12:
                        enabled12 = "<:icons_Correct:921574654307610715>"
                        enabled_count += 1
                    else:
                        enabled12 = "<:icons_Wrong:921574675639840838>"
                        disabled_count += 1

                    if "Enabled" in data13:
                        enabled13 = "<:icons_Correct:921574654307610715>"
                        enabled_count += 1
                    else:
                        enabled13 = "<:icons_Wrong:921574675639840838>"
                        disabled_count += 1

                    if "Enabled" in data14:
                        enabled14 = "<:icons_Correct:921574654307610715>"
                        enabled_count += 1
                    else:
                        enabled14 = "<:icons_Wrong:921574675639840838>"
                        disabled_count += 1

                    if "Enabled" in data15:
                        enabled15 = "<:icons_Correct:921574654307610715>"
                        enabled_count += 1
                    else:
                        enabled15 = "<:icons_Wrong:921574675639840838>"
                        disabled_count += 1

                    if "Enabled" in data16:
                        enabled16 = "<:icons_Correct:921574654307610715>"
                        enabled_count += 1
                    else:
                        enabled16 = "<:icons_Wrong:921574675639840838>"
                        disabled_count += 1
                    limits = await self.limits.find_one({ "guild_id": ctx.guild.id})
                    if limits:
                        embed = discord.Embed(title="Antinuke Settings:", description="```Types: normal, guild```", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                        embed.add_field(name="__Normal:__", value=f"**dangerous_perms:** {enabled}\n**create_roles:** {enabled1} **| Limit:** ``{limits['--create_roles']}/35s``\n**create_channels:** {enabled2} **| Limit:**`` {limits['--create_channels']}/35s``\n**delete_channels:** {enabled3} **| Limit:**`` {limits['--delete_channels']}/35s``\n**delete_roles:** {enabled4} **| Limit:**`` {limits['--delete_roles']}/35s``\n**ban_members:** {enabled5} **| Limit:**`` {limits['--ban_members']}/35s``\n**kick_members:** {enabled6} **| Limit:**`` {limits['--kick_members']}/35s``\n**add_bot:** {enabled7} **| Limit**`` N/A``\n**mention_everyone:** {enabled8} **| Limit:**`` {limits['--mention_everyone']}/35s``\n**create_webhooks:** {enabled9} **| Limit:**`` {limits['--create_webhooks']}/35s``\n**create_threads:** {enabled10} **| Limit:**`` N/A``", inline=True)
                        embed.add_field(name="__Guild:__", value=f"**change_vanity:** {enabled11} **| Limit:**`` N/A``\n**change_icon:** {enabled12} **| Limit:**`` N/A``\n**change_verification:** {enabled13} **| Limit:**`` N/A``\n**change_name:** {enabled14} **| Limit:**`` N/A``\n**change_rules:** {enabled15} **| Limit:**`` N/A``\n**change_banner:** {enabled16} **| Limit:**`` N/A``", inline=True)
                        embed.add_field(name="__Info__", value=f"```ruby\n📁 {ctx.guild.id}\n ↳ Penalty: {penalty}\n ↳ backupLimit: 2\n  ↳ Whitelisted: {dataa['whitelisted']}\n   ↳ Admins: {dataa['owners']}```", inline=False)
                        embed.set_footer(text=f"✅ {enabled_count} trigger(s) enabled | ❌ {disabled_count} trigger(s) disabled")
                        return await ctx.send(embed=embed)
                    else:
                        return await util.send_blurple(ctx, f"Use ``antinuke limitsetup`` first, then use this command. Sorry for the inconvenience.")
            else:
                return await ctx.send("Only ``antinuke admins`` have access to this command.")
        except Exception as e:
            print(e)
            return await ctx.send("The antinuke is not enabled")

    @antinuke.command(
        aliases = ["punishment", "action"],
        usage = "Guild owner, Administrator",
        description = "Set's the antinukes punishment (action) it will take upon an event being triggered",
        brief = "penalty",
        help = "```Syntax: antinuke penalty [penalty]\nExample #1: antinuke penalty kick\nExample #2: antinuke penalty ban\nExample #3: antinuke penalty strip-roles```"
        )
    async def penalty(self, ctx, punishment):
        try:
            dataa = await self.db.find_one({ "guild_id": ctx.guild.id })
            checker = dataa['owners']
            punishments=['ban', 'kick']
            if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers or ctx.author.id in checker:
                if punishment.lower() in punishments:
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "punishment": f"{punishment.lower()}"}})
                    self.cachePunishments.restart()
                    return await util.send_blurple(ctx, f'The antinuke will now ``{punishment.lower()}`` from any ``unwhitelisted`` users.')
                if "strip" in punishment.lower():
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "punishment": "strip-roles"}})
                    self.cachePunishments.restart()    
                    return await util.send_blurple(ctx, 'The antinuke will now ``strip-roles`` from any ``unwhitelisted`` users.')
                else:
                    return await util.send_error(ctx, "That punishment is not supported.")
            else:
                await util.send_issue(ctx, "Only ``antinuke admins`` have access to this command.")
        except Exception as e:
            return await util.send_error(ctx, "The antinuke is not enabled")

    @antinuke.command(
        usage = "Guild owner, Administrator",
        description = "Prevents bots from being invited to your server",
        trigger = 'state',
        help = "```Syntax: antinuke botadd [status (on or off)]\nExample: antinuke botadd off```"
    )
    async def botadd(self, ctx, state:bool):
        try:
            dataa = await self.db.find_one({ "guild_id": ctx.guild.id })
            checker = dataa['owners']
            if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers or ctx.author.id in checker:
                if state == True:
                    status = "Enabled"
                else:
                    status = "Disabled"
                await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { f"--add_bot": f"{status}"}})
                self.cacheSettings.restart()
                return await util.send_blurple(ctx, f"The trigger: `--add_bot` is now  `{status.lower()}` in this server.")
            else:
                return await util.send_error(ctx, "Only ``antinuke admins`` have access to this command.")
        except Exception as e:
                return await util.send_issue(ctx, "The ``antinuke`` is not enabled in this server.")  

    @antinuke.command(
        usage = "Guild owner, Administrator",
        description = "Prevents roles from being mass deleted in your server",
        trigger = 'state',
        help = "```Syntax: antinuke role [status (on or off)]\nExample: antinuke role off```"
    )
    async def role(self, ctx, state:bool):
        try:
            dataa = await self.db.find_one({ "guild_id": ctx.guild.id })
            checker = dataa['owners']
            if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers or ctx.author.id in checker:
                if state == True:
                    status = "Enabled"
                else:
                    status = "Disabled"
                await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { f"--delete_roles": f"{status}"}})
                self.cacheSettings.restart()
                return await util.send_blurple(ctx, f"The trigger: `--delete_roles` is now  `{status.lower()}` in this server.")
            else:
                return await util.send_error(ctx, "Only ``antinuke admins`` have access to this command.")
        except Exception as e:
                return await util.send_issue(ctx, "The ``antinuke`` is not enabled in this server.")  

    @antinuke.command(
        aliases = ['channels'],
        usage = "Guild owner, Administrator",
        description = "Prevents channels from being mass deleted in your server",
        trigger = 'state',
        help = "```Syntax: antinuke channel [status (on or off)]\nExample: antinuke channel off```"
    )
    async def channel(self, ctx, state:bool):
        try:
            dataa = await self.db.find_one({ "guild_id": ctx.guild.id })
            checker = dataa['owners']
            if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers or ctx.author.id in checker:
                if state == True:
                    status = "Enabled"
                else:
                    status = "Disabled"
                await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { f"--delete_channels": f"{status}"}})
                self.cacheSettings.restart()
                return await util.send_blurple(ctx, f"The trigger: `--delete_channels` is now  `{status.lower()}` in this server.")
            else:
                return await util.send_error(ctx, "Only ``antinuke admins`` have access to this command.")
        except Exception as e:
                return await util.send_issue(ctx, "The ``antinuke`` is not enabled in this server.") 

    @antinuke.command(
        usage = "Guild owner, Administrator",
        description = "Prevents members from being mass kicked in your server",
        trigger = 'state',
        help = "```Syntax: antinuke kick [status (on or off)]\nExample: antinuke kick off```"
    )
    async def kick(self, ctx, state:bool):
        try:
            dataa = await self.db.find_one({ "guild_id": ctx.guild.id })
            checker = dataa['owners']
            if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers or ctx.author.id in checker:
                if state == True:
                    status = "Enabled"
                else:
                    status = "Disabled"
                await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { f"--kick_members": f"{status}"}})
                self.cacheSettings.restart()
                return await util.send_blurple(ctx, f"The trigger: `--kick_members` is now  `{status.lower()}` in this server.")
            else:
                return await util.send_error(ctx, "Only ``antinuke admins`` have access to this command.")
        except Exception as e:
                return await util.send_issue(ctx, "The ``antinuke`` is not enabled in this server.") 

    @antinuke.command(
        usage = "Guild owner, Administrator",
        description = "Prevents members from being mass banned in your server",
        trigger = 'state',
        help = "```Syntax: antinuke ban [status (on or off)]\nExample: antinuke ban off```"
    )
    async def ban(self, ctx, state:bool):
        try:
            dataa = await self.db.find_one({ "guild_id": ctx.guild.id })
            checker = dataa['owners']
            if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers or ctx.author.id in checker:
                if state == True:
                    status = "Enabled"
                else:
                    status = "Disabled"
                await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { f"--ban_members": f"{status}"}})
                self.cacheSettings.restart()
                return await util.send_blurple(ctx, f"The trigger: `--ban_members` is now  `{status.lower()}` in this server.")
            else:
                return await util.send_error(ctx, "Only ``antinuke admins`` have access to this command.")
        except Exception as e:
                return await util.send_issue(ctx, "The ``antinuke`` is not enabled in this server.")

    @antinuke.command(
        usage = "Guild owner, Administrator",
        description = "Prevents webhooks from being mass created in your server",
        trigger = 'state',
        help = "```Syntax: antinuke webhook [status (on or off)]\nExample: antinuke webhook off```"
    )
    async def webhook(self, ctx, state:bool):
        try:
            dataa = await self.db.find_one({ "guild_id": ctx.guild.id })
            checker = dataa['owners']
            if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers or ctx.author.id in checker:
                if state == True:
                    status = "Enabled"
                else:
                    status = "Disabled"
                await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { f"--create_webhooks": f"{status}"}})
                self.cacheSettings.restart()
                return await util.send_blurple(ctx, f"The trigger: `--create_webhooks` is now  `{status.lower()}` in this server.")
            else:
                return await util.send_error(ctx, "Only ``antinuke admins`` have access to this command.")
        except Exception as e:
                return await util.send_issue(ctx, "The ``antinuke`` is not enabled in this server.")

    @antinuke.command(
        usage = "Guild owner, Administrator",
        description = "Prevents your vanity URL from being changed in your server",
        trigger = 'state',
        help = "```Syntax: antinuke vanity [status (on or off)]\nExample: antinuke vanity off```"
    )
    async def vanity(self, ctx, state:bool):
        try:
            dataa = await self.db.find_one({ "guild_id": ctx.guild.id })
            checker = dataa['owners']
            if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers or ctx.author.id in checker:
                if state == True:
                    status = "Enabled"
                else:
                    status = "Disabled"
                await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { f"--change_guild_vanity": f"{status}"}})
                self.cacheSettings.restart()
                return await util.send_blurple(ctx, f"The trigger: `--change_guild_vanity` is now  `{status.lower()}` in this server.")
            else:
                return await util.send_error(ctx, "Only ``antinuke admins`` have access to this command.")
        except Exception as e:
                return await util.send_issue(ctx, "The ``antinuke`` is not enabled in this server.")

    @antinuke.command(
        usage = "Guild owner, Administrator",
        description = "Prevents mass pinging",
        trigger = 'state',
        help = "```Syntax: antinuke mention [status (on or off)]\nExample: antinuke mention off```"
    )
    async def mention(self, ctx, state:bool):
        try:
            dataa = await self.db.find_one({ "guild_id": ctx.guild.id })
            checker = dataa['owners']
            if ctx.author.id == ctx.guild.owner.id or ctx.author.id in developers or ctx.author.id in checker:
                if state == True:
                    status = "Enabled"
                else:
                    status = "Disabled"
                await self.db2.update_one({ "guild_id": ctx.guild.id }, { "$set": { f"--mention_everyone": f"{status}"}})
                self.cacheSettings.restart()
                return await util.send_blurple(ctx, f"The trigger: `--mention_everyone` is now  `{status.lower()}` in this server.")
            else:
                return await util.send_error(ctx, "Only ``antinuke admins`` have access to this command.")
        except Exception as e:
                return await util.send_issue(ctx, "The ``antinuke`` is not enabled in this server.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def data(self, ctx, guild_id=None):
        if ctx.author.id in developers:
            try:
                check = await self.db.find_one({ "guild_id": int(guild_id) })
                if guild_id is None:
                    await ctx.send("provide a ``guild_id`` to search for")
                elif guild_id:
                        document = await self.db.find_one({ "guild_id": int(guild_id) })
                        return await ctx.send(f"```json\n{document}\n```")
                if check:
                    return await ctx.send(f"No records found for: ```{guild_id} ```")
            except Exception as e:
                print(e)
        else:
            return


        



async def setup(bot):
    await bot.add_cog(antiEvents(bot))