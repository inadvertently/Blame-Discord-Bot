import discord, aiohttp, asyncio, os
from discord.ext import commands, tasks
from Core.utils import get_theme
from datetime import datetime
import Core.utils as util
from Core.utils import get_theme

async def get_twitch_token():
    async with aiohttp.ClientSession() as session:
        async with session.post('https://id.twitch.tv/oauth2/token',
        data={'client_id': os.environ.get("TWITCH_CLIENT_ID"),
        'client_secret': os.environ.get("TWITCH_CLIENT_SECRET"),
        'grant_type': 'client_credentials'}) as r:
            retrieve = await r.json()
            access_token = retrieve['access_token']
            return access_token

async def return_json(user: str):
    headers = {
        'Client-ID' : os.environ.get("TWITCH_CLIENT_ID"),
        'Authorization' :  "Bearer " + await get_twitch_token()
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.twitch.tv/helix/streams?user_login={user}", headers=headers) as request:
            return await request.json()


class twitchlog(commands.Cog):
    def __init__(self, client):
        self.bot = client
        self.twitches = self.bot.db['twitch']
        self.ratelimit = []
        self.twitch_color = 0x6441a4
        self.twitch_worker.start()
        self.clear_ratelimit.start()
        #self.twitch_background.start()
    
    @tasks.loop(hours=4)
    async def clear_ratelimit(self):
        self.ratelimit.clear()
    
    @clear_ratelimit.before_loop
    async def before_clear_ratelimit(self):
        await self.bot.wait_until_ready()


    @tasks.loop(minutes=15)
    async def twitch_worker(self):
        requests_to_send = self.twitches.find({})
        if requests_to_send:
            for data in await requests_to_send.to_list(length=1000):
                streamers = data['streamer']
                messages = data['message']
                #channels = data['channel']
                true = self.bot.get_channel(data['channel'])
                if true is None:
                    await self.twitches.delete_one({'channel': data['channel']})
                else:
                    base = await return_json(streamers)
                    await asyncio.sleep(2)
                    if len(base['data']) and streamers and true.id and not true.id in self.ratelimit:
                        base = base['data'][0]
                        name = base.get('user_name')
                        description = base.get('description')
                        avatar = base.get('profile_image_url')
                        views = base.get('viewer_count')
                        thumbnails = base.get('thumbnail_url')
                        thumbnail = thumbnails.replace('-{width}x{height}', '')
                        game = base.get('game_name')
                        title = base.get('title')
                        time = base.get('started_at')
                        timestamp = time
                        formatt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
                        d =discord.utils.format_dt(formatt, style='t')
                        embed = discord.Embed(color=self.twitch_color)
                        embed.set_author(name=f"{name} is now live on Twitch!", icon_url=thumbnail) 
                        embed.url = f"https://twitch.tv/{streamers}"
                        embed.title = f"{title}"
                        embed.description = f"Playing **{game}**! for **{views:,}** viewers\n[Watch Stream](https://twitch.tv/{streamers})"
                        embed.set_image(url=thumbnail)
                        embed.set_footer(text=f"blame.gg ・")
                        if messages:
                            if "{streamer}" in messages:
                                messages = messages.replace("{streamer}", str(name))
                            if "{views}" in messages:
                                messages = messages.replace("{views}", str(views))
                            if "{view_count}" in messages:
                                messages = messages.replace("{view_count}", str(views))
                            if "{game}" in messages:
                                messages = messages.replace("{game}", str(game))
                            if "{game_name}" in messages:
                                messages = messages.replace("{game_name}", str(game))
                            if "{title}" in messages:
                                messages = messages.replace("{title}", str(title))
                            if "{link}" in messages:
                                messages = messages.replace("{link}", f"https://twitch.tv/{streamers}")
                            if "{twitch_link}" in messages:
                                messages = messages.replace("{twitch_link}", f"https://twitch.tv/{streamers}")
                            await true.send(content=messages, embed=embed)
                        else:
                            await true.send(embed=embed)
                        self.ratelimit.append(true.id)
                    else:
                        pass
    
    @twitch_worker.before_loop
    async def before_twitch_worker(self):
        await self.bot.wait_until_ready()

    @commands.group(
        invoke_without_command=True,
        usage = 'send_messages',
        brief = "subcommand",
        description = "Get notifications sent to a channel when a streamer goes live!",
        help = "```Syntax: twitch [subcommand]\nExample: twitch add #notifications KaiCenat ```"
    )
    async def twitch(self, ctx, user):
        try:
            async with ctx.typing():
                head = {
                    'Client-ID' : os.environ.get("TWITCH_CLIENT_ID"),
                    'Authorization' :  "Bearer " + await get_twitch_token()
                    }
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'https://api.twitch.tv/helix/users?login={user}', headers=head) as r:
                        if r.status == 200:
                            json = await r.json()
                            id = json['data'][0]['id']
                            name = json['data'][0]['display_name']
                            bio = json['data'][0]['description']
                            pic = json['data'][0]['profile_image_url']
                            banner = json['data'][0]['offline_image_url']
                            views = json['data'][0]['view_count']
                            embed = discord.Embed(title=name, url=f"https://twitch.tv/{name}", timestamp = ctx.message.created_at, color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                            embed.set_author(name=f"Twitch lookup ・ {user}", icon_url="https://cdn.discordapp.com/attachments/851633587915587615/1016543428076650526/twitch.png")
                            #embed.set_image(url=banner)
                            embed.description = f"**{bio}**"
                            embed.set_thumbnail(url=pic)
                            embed.set_footer(text=f"ID: {id}・🔗 {views} ")
                            await ctx.send(embed=embed)
                        else:
                            return await ctx.send('404: Not Found')
        except:
            pass
            return await util.send_command_help(ctx)
    
    @twitch.command(
        usage = 'manage_channels',
        brief = "channel, streamer",
        description = "Get notifications sent to a channel when a streamer goes live!",
        help = "```Syntax: twitch add [channel] [streamer]\nExample: twitch add #notifications KaiCenat ```"
    )
    @commands.has_permissions(manage_channels=True)
    async def add(self, ctx, channel: discord.TextChannel, streamer: str):
        check = await self.twitches.count_documents({'guild_id': ctx.guild.id, "streamer": streamer})
        if not check:
            head = {
                'Client-ID' : os.environ.get("TWITCH_CLIENT_ID"),
                'Authorization' :  "Bearer " + await get_twitch_token()
                }
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.twitch.tv/helix/users?login={streamer}', headers=head) as r:
                    resp = await r.json()
                    if len(resp['data']):
                        await util.send_blurple(ctx, f"``{streamer}`` will now be streamed to {channel.mention}!")
                        return await self.twitches.insert_one({
                            'guild_id': ctx.guild.id,
                            'channel': channel.id,
                            'message': None,
                            'streamer': streamer
                        })
                    else:
                        return await util.send_issue(ctx, f"``{streamer}`` is an invalid twitch account!")
        if check > 1:
            return await ctx.send(embed=discord.Embed(description=f":star: To set more than ``2`` streaming channels, you must upgrade to **[premium](http://discord.gg/blame)**", color=0x43B581))

    @twitch.command(
        usage = 'manage_channels',
        brief = "channel, streamer",
        description = "Remove notifications from being sent to a stream channel",
        help = "```Syntax: twitch remove [channel] [streamer]\nExample: twitch remove #notifications KaiCenat ```"
    )
    @commands.has_permissions(manage_channels=True)
    async def remove(self, ctx, channel: discord.TextChannel, streamer: str):
        check = await self.twitches.count_documents({'guild_id': ctx.guild.id, 'channel': channel.id, 'streamer': streamer})
        if check:
            await util.send_blurple(ctx, f"``{streamer}`` will no longer be streamed to {channel.mention}")
            return await self.twitches.delete_one({'guild_id': ctx.guild.id, 'channel': channel.id, 'streamer': streamer})
        else:
            return await util.send_issue(ctx, f"``{streamer}`` does not have streaming set to {channel.mention}")

    @twitch.command(
        usage = 'manage_channels',
        brief = 'message',
        description = 'Set the twitch notifcation message that appears above the embed or view your current one.',
        help = "```Syntax: twitch message [message]\nExample: twitch message @notifications {streamer} is now live!``` "
    )
    @commands.has_permissions(manage_channels=True)
    async def message(self, ctx, *, message=None):
        check = await self.twitches.find_one({'guild_id': ctx.guild.id})
        if check:
            if check['message'] is not None and message is None:
                return await util.send_blurple(ctx, f"Your current twitch message is set as:\n```ruby\nmessage: {check['message']}\n```")
            if check['message'] is None and message:
                await util.send_blurple(ctx, f"The notification message has been set to:\n```ruby\nmessage: {message}\n```")
                return await self.twitches.update_many({ "guild_id": ctx.guild.id }, { "$set": { "message": f"{message}"}})
            if check['message'] is not None and message:
                await util.send_blurple(ctx, f"The notification message has been set to:\n```ruby\nmessage: {message}\n```")
                return await self.twitches.update_many({ "guild_id": ctx.guild.id }, { "$set": { "message": f"{message}"}})
            else:
                return await util.send_command_help(ctx)
        else:
            return await util.send_issue(ctx, f"You must first set a streamer channel with ``{ctx.prefix} twitch add [channel] [streamer]``")

    @twitch.command(
        aliases =  ['list'],
        usage = 'manage_channels',
        brief = 'None',
        description = 'View the streamer channels you have set',
        help = "```Example: twitch view``` "
    )
    async def view(self, ctx):
        check = await self.twitches.find_one({'guild_id': ctx.guild.id})
        if check:
            fetch = self.twitches.find({'guild_id': ctx.guild.id})
            streamers = []
            channels = []
            for data in await fetch.to_list(length=5):
                streamers.append(data['streamer'])
                channels.append(data['channel'])
            resp = [f"``{streamers}`` set for <#{channels}>" for streamers, channels in zip(streamers, channels)]
            rows = []
            content = discord.Embed(description="", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
            content.set_author(name=f"Twitch notifications in {ctx.guild.name} ({ctx.guild.id})", icon_url="https://cdn.discordapp.com/attachments/851633587915587615/1042947928798535791/twitch.png")
            for count, i in enumerate(resp, start=1):
                rows.append(f"**{count}.)** {i}")
            await util.send_as_pages(ctx, content, rows)
        else:
            return util.send_issue(ctx, f"There are no stream channels set in this server.")








async def setup(bot):
    await bot.add_cog(twitchlog(bot))