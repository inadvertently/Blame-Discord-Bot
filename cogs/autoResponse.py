import discord, motor, asyncio, Core.utils as util, Core.confirm as cop_is_gae, Core.utils as utils
from discord.ext import commands
from discord.ext.commands import BucketType
from typing import List
import discord.ui, re
from datetime import datetime
from Core.utils import get_theme
from yt_dlp import YoutubeDL
import glob, os, time
from moviepy.editor import *
import requests
from io import BytesIO

regexes = [
    'https:\/\/www\.instagram\.com\/reel\/([a-zA-Z0-9_\-]*)',
    'https:\/\/www\.tiktok\.com\/@[A-z]*\/video\/([a-zA-Z0-9_\-]*)',
]
regexes = [re.compile(s) for s in regexes]

async def check_url(message_content):
    """Check if message content is a URL. If so, return video url and id."""

    for regex in regexes:
        matches = re.search(regex, message_content)

        if matches:
            state = bool(matches)
            url = matches[0]
            id = matches[1]
            return state, url, id

    return False, None, None




class autoResponsE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db['autoResponder']


    @commands.group(
        aliases = ['ar'],
    usage = "Manage_guild",
    description = "Set a trigger (sentence or word seperated by a comma) in which the bot will respond to with a custom response",
    brief = "subcommand, argument, subarg[Optional]",
    help = "```Syntax: autoresponder [subcommand] <argument>\nExample: autoresponder add hi, sup```"
    )
    async def autoresponder(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Command: autoresponder", description="Module that allows you to set custom trigger words that it'll then respond to with custom responses.\n```Syntax: autoresponder [subcommand] <argument>\nExample: autoresponder add [trigger] [response]```", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                embed.set_author(name="autoresponder help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('autoresponder').walk_commands()])} ・ autoresponder")
                return await ctx.send(embed=embed)
        except Exception as e:
            print(e)

    @autoresponder.command(
        name='add',
        usage = 'Manage guild',
        description = "Set a trigger (sentence or word seperated by a comma) in which the bot will respond to with a custom response",
        brief = "trigger, response",
        help = "```Syntax: autoresponder add [trigger], [response]\nExample: autoresponder add pic perms, level 5 for them```"
        
        )
    @commands.has_permissions(manage_guild=True)
    async def ad(self, ctx, *, resp):
        check = await self.db.count_documents({ "guild_id": ctx.guild.id })
        trigger, response = resp.split(",")
        now = datetime.now()
        dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
        if check == 10:
            return await ctx.send("you cant have more than 10 autoresponses per guild")
        if not check:
            #trigger, response = resp.split(",")
            if trigger == None:
                return await ctx.send("need a trigger and response")
            if response == None:
                return await ctx.send("need a response")
            if len(response) > 100:
                return await ctx.send("Response cannot be longer than 100 characters.")
            if len(trigger) > 20:
                return await ctx.send("Trigger cannot be longer than 20 characters.")
            else:
                msg = discord.Embed(description='this is your 1st time using autoresponder.. building structure')
                msgsend = await ctx.send(embed=msg)
                await asyncio.sleep(1.2)
                await self.db.insert_one({
                "guild_id": ctx.guild.id,
                "trigger": str(trigger),
                "response": str(response),
                "author": str(ctx.author.id),
                "time": str(dt_string)
                })
                msg2 = discord.Embed(description=f"<:check:921544057312915498> **{trigger}** will now be **responded** to with **{response}**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                msg2.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                return await msgsend.edit(embed=msg2)
        else:
            if trigger == None:
                return await ctx.send("need a trigger and response")
            if response == None:
                return await ctx.send("need a response")
            if trigger and response:
                check_existing = await self.db.find_one({ "guild_id": ctx.guild.id })
                data = check_existing["trigger"]
                if trigger in data:
                    return await ctx.send("this trigger alrdy exists")
                if len(response) > 100:
                    return await ctx.send("Response cannot be longer than 100 characters.")
                if len(trigger) > 20:
                    return await ctx.send("Trigger cannot be longer than 20 characters.")
                else:
                    await self.db.insert_one({
                    "guild_id": ctx.guild.id,
                    "trigger": str(trigger),
                    "response": str(response),
                    "author": str(ctx.author.id),
                    "time": str(dt_string)
                    })
                    msg2 = discord.Embed(description=f"<:check:921544057312915498> **{trigger}** will now be **responded** to with **{response}**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                    msg2.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                    return await ctx.send(embed=msg2)
            else:
                return await ctx.send("something went wrong, report this pls")

    @autoresponder.command(
        name='remove',
        usage = 'Manage guild',
        description = "Remove an autoresponder from your guild ",
        brief = "trigger",
        help = "```Syntax: autoresponder remove [trigger]\nExample: autoresponder remove wlc```"
        )
    @commands.has_permissions(manage_guild=True)
    async def re(self, ctx, trigger=None):
        if trigger:
            check = await self.db.count_documents({ "guild_id": ctx.guild.id })
            if check:
                check_existing = await self.db.find_one({ "guild_id": ctx.guild.id, "trigger": str(trigger)  })
                if check_existing:
                    await self.db.delete_one({ "guild_id": ctx.guild.id,  "trigger": str(trigger) })
                    return await ctx.send(f"Autoresponse trigger **{trigger}** has been removed")
                else:
                    return await ctx.send(f"The trigger **{trigger}** does not exist ")

                #
            else:
                return await ctx.send("There are no autoresponders in this guild")
        else:
            return await ctx.send("need trigger")


    @autoresponder.command(
        name = "list",
        usage = "Manage guild",
        description = "View all the autoresponders in your guilds database.",
        brief = "None",
        help = "```Example: autoresponder list```"
    )
    @commands.has_permissions(manage_guild=True)
    async def ls(self, ctx):
        check = await self.db.count_documents({ "guild_id": ctx.guild.id })
        try:
            if check:
                check_existing = self.db.find({ "guild_id": ctx.guild.id})
                triggers = []
                responses = []
                authors = []
                time = []
                for doc in await check_existing.to_list(length=15):
                    trigs = doc["trigger"]
                    resps = doc["response"]
                    auths = doc["author"]
                    dates = doc["time"]
                    triggers.append(trigs)
                    responses.append(resps)
                    authors.append(auths)
                    time.append(dates)
                responseStr = [f""""**{triggers}**" \➡️ **Creator:** <@{authors}>, ``({time})``""" for triggers, authors, time in zip(triggers, authors, time)]
                rows = []
                content = discord.Embed(title=f"Auto Responses:", description="")
                content.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
                content.color= int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)

                for count, i in enumerate(responseStr, start=1):
                    rows.append(f"``{count})`` {i}")
                content.set_footer(text=f"({count}/{count}) autoresponses")
                await util.send_as_pages(ctx, content, rows)
            else:
                return await ctx.send("No autoresponders in this guild") 
        except Exception as e:
            print(e)


    @autoresponder.command(
        name='clear',
        usage = "Manage guild",
        description = "Clear all the current autoresponses in your server.",
        brief = "None",
        help = "```Example: autoresponder clear```"
    )
    @commands.has_permissions(manage_guild=True)
    async def cl(self, ctx):
        check = await self.db.count_documents({ "guild_id": ctx.guild.id })
        if check:
            yes = discord.Embed(description="Are u sure u want to clear this guilds autoresponders?")
            msg = await ctx.send(embed=yes)
            async def confirm():
                await self.db.delete_many({ "guild_id": ctx.guild.id })
                await msg.edit(view=None, embed=discord.Embed(description="All of this server's autoresponders have been removed.", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
            async def cancel():
                await msg.edit(view=None, embed=discord.Embed(description="The autoresponder clear process has been cancelled", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                pass
            confirmed:bool = await cop_is_gae.confirm(self, ctx, msg)
            if confirmed:
                await confirm()
            else:
                await cancel()
        else:
            await ctx.send("this guild has no autoresponders")





    @commands.command(aliases = ['instagram', 'reel'])
    @commands.cooldown(3, 14, BucketType.user)
    async def ig(self, ctx, message):
        async with ctx.typing():
            try:
                state, url, id = await check_url(message)
                if state:
                    timer = time.time()
                    async def download(url, filename):
                        ydl = YoutubeDL({
                            'outtmpl': f'reel/{filename}.%(ext)s',
                            'format': 'bestaudio/best'
                        })
                        ydl.download([str(url)])
                        path = glob.glob(f'reel/{filename}.*')[0]
                        clip = VideoFileClip(path)
                        clip1 = clip.subclip(0, 7)
                        w1 = clip1.w
                        h1 = clip1.h
                        print("Width x Height of clip 1 : ", end = " ")
                        print(str(w1) + " x ", str(h1))
                        print("---------------------------------------")
                        clip2 = clip1.resize(0.8)
                        w2 = clip2.w
                        h2 = clip2.h
                        print("Width x Height of clip 2 : ", end = " ")
                        print(str(w2) + " x ", str(h2))
                        a = clip2.write_videofile("assets/gfg_intro.mp4", threads = 12, fps=24, audio=True)
                    async def binary():
                        with open("assets/gfg_intro.mp4", "rb") as fh:
                            return BytesIO(fh.read())
                    await download(url, id)
                    await ctx.send(file=discord.File(fp=await binary(), filename="assets/gfg_intro.mp4"))
                    await ctx.send(f"Took ``{time.time() - timer} seconds``")
                    os.remove("assets/gfg_intro.mp4")  
                else:
                    return await ctx.send("error")
            except Exception as e:
                return await ctx.send("failed to parse")
        


    



async def setup(bot):
    await bot.add_cog(autoResponsE(bot))