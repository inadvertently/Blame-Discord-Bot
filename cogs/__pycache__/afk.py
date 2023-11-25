import discord, requests, datetime, time, urbandict, random, asyncio, json, re, sys, os, youtube_dl, threading, math
from threading import Thread
from random import randint
from datetime import datetime
from discord.ext import commands, tasks
from discord.utils import get
from discord.errors import ClientException

errorcol = 0xA90F25
success = discord.Colour.blurple()
errmsg = "<:yy_yno:921559254677200957> Internal server error occured. Report this [here](https://discord.gg/k9q6JUBHwP)"
path = os.path.dirname(os.path.abspath(__file__))

def register(file, guild):
    try:
        with open(file, 'r+') as f:
            data = json.load(f)
        if str(guild.id) not in list(data):
            data[str(guild.id)] = {
                "AFK": {}
            }
            with open(file, 'w') as f:
                json.dump(data, f, indent = 4)
    except:
        pass

class afk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.oldtime = datetime.now()
 

         #em = discord.Embed(
            #colour = 0x2f3136
        #)
        #em = discord.Embed(title=f" __**Blame's Help Panel**__ {discstaff}", color=0x2f3136, timestamp=ctx.message.created_at)


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[\x1b[38;5;213mBlame\x1b[38;5;15m] Cog Loaded: [\x1b[38;5;213m{self.__class__.__name__}\x1b[38;5;15m]")

    @commands.command()
    async def AFK(self, ctx, *, reason=None):
        if reason == None:
            em = discord.Embed(description=f"> afk", color=success)
            em.set_author(name=f"{ctx.message.author} is now afk with the status..")
            reason = ''
            await ctx.reply(embed=em)
        else:
            emm = discord.Embed(description=f"> {reason}", color=success)
            emm.set_author(name=f"{ctx.message.author} is now afk with the status..")
            await ctx.reply(embed=emm)
        with open(path+r'/enabled.json', "r") as f:
            data = json.load(f)
        print(list(data[str(ctx.guild.id)]['AFK']))
        if str(ctx.author.id) in list(data[str(ctx.guild.id)]['AFK']):
            await ctx.channel.send('Slow down you :monkey:')
            return


        
        data[str(ctx.guild.id)]['AFK'][str(ctx.author.id)] = reason

        

        with open(path+r'/enabled.json', "w") as f:
            json.dump(data,f, indent = 4)
        #try:
            #await ctx.author.edit(nick='[AFK]'+ctx.author.name)
        #except:
            #pass
    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            register(path+r'/enabled.json', message.guild)
            if message.content.startswith('-'): 
                return
            with open(path+r'/enabled.json', "r") as f:
                data = json.load(f)
            
            if str(message.author.id) in list(data[str(message.guild.id)]['AFK']):
                data[str(message.guild.id)]["AFK"].pop(str(message.author.id))
                with open(path+r'/enabled.json', "w") as f:
                    json.dump(data, f, indent=4)
                emsy = discord.Embed(description=f"<a:wave:926523917382852638> <@{message.author.id}> weclome back, I removed your AFK", color=success)
                emsy.set_author(name=f"{message.author} is no longer afk...")
                #await message.author.edit(nick=message.author.name)
                await message.channel.send(embed=emsy)
                
            for i in message.mentions:
                if str(i.id) in list(data[str(message.guild.id)]['AFK']):
                    if data[str(message.guild.id)]['AFK'][str(i.id)] != '':
                        reason = data[str(message.guild.id)]['AFK'][str(i.id)]
                    else:
                        reason = ''
                    time = datetime.now() - self.oldtime
                    ems = discord.Embed(description=f"> {reason}", color=success)
                    ems.set_author(name=f"{i.name} is afk with the status.. ")
                    await message.channel.send(embed=ems)
                    break
        except:
            pass

def setup(bot):
    bot.add_cog(afk(bot))