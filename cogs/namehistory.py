import discord, db.database as database, random, typing, Core.utils as util
import discord, os, asyncio, motor, orjson
from datetime import datetime
from discord.ext import commands
from colorama import init
from termcolor import colored
from colorama import Fore as f

class nameHistorY(commands.Cog):
    def __init__(self, client):
        self.bot = client 
        self.db = self.bot.db['nameHistory']
        self.status = {}

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        now = datetime.now()
        statuses = ['online', 'dnd', 'idle']
        #dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
        if before.name != after.name:
            try:
                finduser = await self.db.find_one({"User": f"{before.id}"})
                if finduser:
                    await self.db.update_one({ "User": f"{before.id}" }, { "$push": { "nameHistory": f""" "{after.name}" \➡️ [``{dt_string}``]""" }})
                    #print(colored(f"[LOGGED] | ENTRY FOR: [{before.name}] -> [{after.name}] | TYPE: USER", 'yellow'))
                else:
                    await self.db.insert_one({
                        "User": f'{before.id}',
                        "nameHistory": [f""" "{before.name}" \➡️ [``{dt_string}``] """, f""" "{after.name}" \➡️ [``{dt_string}``]"""]
                        })
                    #print(colored(f'[CREATED] | ENTRY FOR: [{before.name}] -> [{after.name}] | TYPE: USER', 'red'))      
            except Exception:
                pass; return
        else:
            return

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        now = datetime.now()
        statuses = ['online', 'dnd', 'idle']
        if str(before.status) in statuses and str(after.status) == 'offline':
            self.status[str(before.id)] = now
        if str(before.status) == 'offline' and str(after.status) in statuses:
            self.status[str(before.id)] = now
        else:
            return

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        now = datetime.now()
        self.status[str(user.id)] = now
    
    @commands.command(
        aliases = ['nhistory', 'names', 'allnames', 'recentnames', 'nh'],
        usage = 'Send Messages',
        description = "View all of your past usernames the bot has been able to gather",
        brief = 'None',
        help = "```Example: names\nBot output: Here are your past usernames\n```"

    )
    async def namehistory(self, ctx, user: discord.User=None):
        try:
            if user is None:
                user = ctx.author
            results = ''
            data = await self.db.find_one({"User": f"{user.id}"})
            if not data:
                return await util.send_issue(ctx, f"No past names logged for ``{user}``")
            else:
                names = data["nameHistory"]
                content = discord.Embed(description="")
                rows= []
                for count, i in enumerate(names, start=1):
                    i=i.split("\➡")
                    rows.append(f"``{count})``{str(i[0])} **-** {i[1]}")
                content.set_footer(text=f'({len(rows)} entries) ∙ Duplicates are not filtered')
                content.set_author(name=f"{user.display_name}'s name history", icon_url=user.display_avatar.url )
                content.color = discord.Color.blurple()
                content.set_thumbnail(url=user.display_avatar.url)
                await util.send_as_pages(ctx, content, rows)
        except Exception as e:
            return

    @commands.command(
        description = 'Clear all your namehistory data',
        brief = 'None',
        usage = 'send_messages',
        help = '```Example: clearnames```'
    )
    async def clearnames(self, ctx):
        data = await self.db.find_one({"User": f"{ctx.author.id}"})
        if data:
            await self.db.delete_many({"User": f"{ctx.author.id}"})
            return await util.send_blurple(ctx, 'All your names have been removed.')
        else:
            return await util.send_issue(ctx, 'No previous names logged for you..')


    @commands.command(aliases=['seen'])
    async def lastseen(self, ctx, user: discord.User=None):
        if user is None:
            user = ctx.author
        try:
            gget={**self.status,**orjson.loads(await self.bot.redis.get("lastseen"))}
            get=gget.get(str(user.id))
        except Exception as e:
            await ctx.send(e)
            return await ctx.send(f"No last seen records for **{user}** have been recorded yet..")
        if get:
            return await ctx.send(f"**{user}** was last seen {discord.utils.format_dt(get, style='R')}")
        else:
            return await ctx.send(f"No last seen records for **{user}** have been recorded yet..")
            

async def setup(client): 
   await client.add_cog(nameHistorY(client))