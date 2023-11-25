
import discord,datetime,time,humanize
from discord import client
from discord.ext import commands, tasks
import json, db.database as db
import time
from Core.utils import get_theme

errorcol = 0xA90F25
success = discord.Colour.blurple()
class AFK(commands.Cog):
    def __init__(self, bot, *args, **kwargs):
        self.bot=bot
        self.db = self.bot.db['afk']
        self.afk = {}
        self.cacheAFK.start()

    @tasks.loop(minutes=20)
    async def cacheAFK(self):
        getAFKS = self.db.find({})
       # guild_ids = []
        user_ids = []
        reasons = []
        times = []
        for i in await getAFKS.to_list(length=9999):
            get_guilds = i['guild_id']
            get_users = i['user_id']
            get_reasons = i['reason']
            get_times = i['time']
            #guild_ids.append(get_guilds)
            user_ids.append(get_users)
            reasons.append(get_reasons)
            times.append(get_times)
        self.afk = {user_ids:{'reason': reasons, 'time': times} for(user_ids, reasons, times) in zip(user_ids, reasons, times)}

    @cacheAFK.before_loop
    async def before_cacheAFK(self):
        await self.bot.wait_until_ready()
    
    @commands.Cog.listener()
    async def on_message(self, message):
        afk = self.afk.get(message.author.id)
        if not message.author.bot and afk is not None:
            times = self.afk[message.author.id]['time']
            meth = int(time.time()) - int(times)
            been_afk_for = humanize.precisedelta(meth)
            embed = discord.Embed(description=f"<a:wave:926523917382852638> <@{message.author.id}> Welcome back! you were **AFK** for: **{been_afk_for}**", color=int(await get_theme(self, bot=self.bot, guild=message.guild.id), 16))
            await message.channel.send(embed=embed)
            await self.db.delete_many({"user_id": message.author.id})
            self.cacheAFK.restart()
                #mentionz = afk[f'{message
        if message.mentions:
            for user_mention in message.mentions:
                get = self.afk.get(user_mention.id)
                if message.author.bot:
                    return
                if get is not None:
                    reason = self.afk[user_mention.id].get('reason')
                    meth = int(time.time()) - int(self.afk[user_mention.id].get('time'))
                    been_afk_for = humanize.naturaltime(meth)
                    embed = discord.Embed(description=f"<:yy_leave:921559236520079430> **{user_mention}** Is currently AFK: **{reason}** - {been_afk_for}", color=int(await get_theme(self, bot=self.bot, guild=message.guild.id), 16))
                    await message.channel.send(embed=embed)
        else:
            return
                
                    


                
        
    @commands.hybrid_command(
        usage = "Send Messages",
        description = "Set an temporary AFK message while you're away.",
        brief= "message",
        help = f"```Syntax: afk [message]\nExample: afk reading a book...```"
        )
    async def afk(self, ctx, *, reason=None):
        if not ctx.me.guild_permissions.embed_links:
            return
        afk = await self.db.find_one({"user_id": ctx.author.id})
        if not reason: 
            reason = 'AFK'
        if afk:
            return await ctx.send("Stop spamming you :monkey:")
        else:
            embed = discord.Embed(description=f"> **{reason}**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
            embed.set_author(name=f"{ctx.message.author} is now afk with the status..")
            await ctx.send(embed=embed)
            await self.db.insert_one({
                "guild_id": ctx.guild.id,
                "user_id": ctx.author.id,
                "reason": str(reason),
                "time": int(time.time())
            })
            self.afk[ctx.author.id]= {"reason": str(reason), "time": int(time.time())}




async def setup(client):
    await client.add_cog(AFK(client))