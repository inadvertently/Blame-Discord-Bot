import discord, db.database as database, random, typing, Core.utils as util
import discord, os, asyncio, motor
from datetime import datetime
from discord.ext import commands
from colorama import init
from termcolor import colored
from colorama import Fore as f


class guildnameHistorY(commands.Cog):
    def __init__(self, client):
        self.bot = client 
        self.db = self.bot.db['guildnameHistory']

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
        if before.name != after.name:
            try:
                findguild = await self.db.find_one({"Guild": f"{before.id}"})
                if findguild:
                    await self.db.update_one({ "Guild": f"{before.id}" }, { "$push": { "guildnameHistory": f""" "{after.name}" \➡️ [``{dt_string}``]""" }})
                    print(colored(f"[LOGGED] | ENTRY FOR: [{before.name}] -> [{after.name}] | TYPE: GUILD", 'green'))
                else:
                    await self.db.insert_one({
                        "Guild": f'{before.id}',
                        "guildnameHistory": [f""" "{before.name}" \➡️ [``{dt_string}``] """, f""" "{after.name}" \➡️ [``{dt_string}``]"""]
                        })
                    print(colored(f'[CREATED] | ENTRY FOR: [{before.name}] -> [{after.name}] | TYPE: GUILD', 'blue'))
            except: pass; return
        else:
            return

    @commands.command(
        aliases = ['ghistory', 'guildnames', 'allguildnames', 'recentguildnames', 'gnames', 'snames', 'servernames'],
        usage = 'Send Messages',
        description = "View all of your guild's (server) past names",
        brief = 'None',
        help = "```Example: guildnames\nBot output: Here are this guilds past names```"

    )
    async def guildhistory(self, ctx):
        results = ''
        data = await self.db.find_one({"Guild": f"{ctx.guild.id}"})
        if not data:
            return await ctx.send('Nothing in db found for this guild')
        else:
            names = data["guildnameHistory"]
            content = discord.Embed(description="")
            rows= []
            for count, i in enumerate(names, start=1):
                i=i.replace(":arrow_right:", "➡")
                rows.append(f"``{count})``{str(i)}")
                #embed.description += f"``{count})``{str(i)}\n"
                #embed.set_footer(text=f"{count} entries ")
            #await ctx.send(embed=embed)
            content.set_footer(text=f'({len(rows)} entries) ∙ Duplicates are not filtered')
            content.set_author(name=f"{ctx.guild.name}'s past guild names", icon_url=ctx.guild.icon.url)
            content.color = discord.Color.blurple()
            content.set_thumbnail(url=ctx.guild.icon.url)
            await util.send_as_pages(ctx, content, rows)
            
        




async def setup(client): 
   await client.add_cog(guildnameHistorY(client))