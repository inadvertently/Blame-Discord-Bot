import discord, aiohttp, random
from discord.ext import commands
from typing import List
import discord.ui
from Core.utils import get_theme


class animefun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.slap = bot.db['slaps']
        self.kiss = bot.db['kisses']
        self.pat = bot.db['pats']
        self.kissresponses = [
            'why the hell are you trying to kiss yourself',
            'dude, find a girlfriend and stop trying to kiss yourself',
            'never do that infront of me ever again',
            'awkward....',
            '*crickets..*',
            '<a:AN_yuh:1017256951874322523> dont kiss yourself..'
        ]
        self.slapresponses = [
            'give me someone to b*tch slap',
            "yea... go ahead and ping who we're b*tch slapping",
            "violence isn't the answer",
            "trust me... this is assualt",
            "PAUSE.. lets think of a more peacful way to settle this..",
            "don't do it.."
        ]
        self.patresponses = [
            '**^.^** give me someone to pat'
        ]

    @commands.command()
    async def kiss(self, ctx, user: discord.Member=None): 
        if user == None:
            return await ctx.send(random.choice(self.kissresponses))
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nekos.life/api/v2/img/kiss") as r:
                res = await r.json()
                em = discord.Embed(description=f"{ctx.author.mention} ***kisses*** {user.mention}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                em.set_image(url=res['url'])
                try:
                    find = await self.kiss.find_one({"author": ctx.author.id, "user": user.id})
                    if find:
                        count = find['count']
                        new_count = count+1
                        print(new_count)
                        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
                        await self.kiss.update_one({"author": ctx.author.id}, {"$set": {"count": new_count}})
                        em.set_footer(text=f"Thats your {ordinal(new_count)} kiss with {user}")
                    if not find:
                        await self.kiss.insert_one({"author": ctx.author.id, "user": user.id, "count":1})
                        em.set_footer(text=f"Thats your 1st kiss with {user}")
                except Exception as e:
                    print(e)
                await ctx.send(embed=em)

    @commands.command()
    async def slap(self, ctx, user: discord.Member=None): 
        if user == None:
            return await ctx.send(random.choice(self.slapresponses))
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nekos.life/api/v2/img/slap") as r:
                res = await r.json()
                em = discord.Embed(description=f"{ctx.author.mention} ****b*tch slaps**** {user.mention}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                em.set_image(url=res['url'])
                try:
                    find = await self.slap.find_one({"author": ctx.author.id, "user": user.id})
                    if find:
                        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
                        count = find['count']
                        new_count = count+1
                        print(new_count)
                        await self.slap.update_one({"author": ctx.author.id}, {"$set": {"count": new_count}})
                        em.set_footer(text=f"Thats your {ordinal(new_count)} slap towards {user}")
                    if not find:
                        await self.slap.insert_one({"author": ctx.author.id, "user": user.id, "count":1})
                        em.set_footer(text=f"Thats your 1st time slapping {user}")
                except Exception as e:
                    print(e)
                await ctx.send(embed=em)

    @commands.command()
    async def pat(self, ctx, user: discord.Member=None): 
        if user == None:
            return await ctx.send(random.choice(self.patresponses))
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nekos.life/api/v2/img/pat") as r:
                res = await r.json()
                em = discord.Embed(description=f"{ctx.author.mention} *pats* {user.mention}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                em.set_image(url=res['url'])
                try:
                    find = await self.pat.find_one({"author": ctx.author.id, "user": user.id})
                    if find:
                        count = find['count']
                        new_count = count+1
                        print(new_count)
                        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
                        await self.pat.update_one({"author": ctx.author.id}, {"$set": {"count": new_count}})
                        em.set_footer(text=f"Thats your {ordinal(new_count)} time you pat {user}")
                    if not find:
                        await self.pat.insert_one({"author": ctx.author.id, "user": user.id, "count":1})
                        em.set_footer(text=f"Thats your 1st time patting {user}")
                except Exception as e:
                    print(e)
                await ctx.send(embed=em)



async def setup(bot):
    await bot.add_cog(animefun(bot))