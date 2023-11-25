import discord
from discord.ext import commands, tasks
from pytz import timezone
from Core import confirm
from Core import utils as util
import typing
import datetime
import random, re, asyncio
from discord import ui
from datetime import timedelta, datetime
import time
from colorama import Fore as f
from Core.utils import get_theme
tz=timezone('EST')

def seconds_until_midnight():
	now = datetime.now(tz)
	target = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
	diff = (target - now).total_seconds()
	return diff

def secs_till_week():
	now = datetime.now(tz)
	target = (now + timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
	diff = (target - now).total_seconds()
	return diff

class membercounts(commands.Cog):
	def __init__(self, client):
		self.bot = client
		self.joins={}
		self.msgs = {}
		self.weekMsgs = {}
		self.weekJoins = {}
		self.called_once_a_day_at_midnight.start()

	@commands.Cog.listener()
	async def on_member_join(self, member):
		try:
			if member.guild.id not in self.joins:
				self.joins[member.guild.id]=[]
				self.weekJoins[member.guild.id]=[]
			try:
				self.joins[member.guild.id]+=1
				self.weekJoins[member.guild.id]+=1
			except:
				self.joins[member.guild.id]=1
				self.weekJoins[member.guild.id]=1
		except:pass;return

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		try:
			if member.guild.id not in self.joins:
				self.joins[member.guild.id]=[]
				self.weekJoins[member.guild.id]=[]
			try:
				self.joins[member.guild.id]-=1
				self.weekJoins[member.guild.id]-=1
			except:
				self.joins[member.guild.id]=-1 
				self.weekJoins[member.guild.id]=-1
		except:pass;return


	@tasks.loop(seconds=1)
	async def called_once_a_day_at_midnight(self):
		await asyncio.sleep(seconds_until_midnight())
		del self.joins
		del self.msgs
		print(f"{f.LIGHTRED_EX}[{f.RESET}{f.BLUE}(Loop Triggered){f.RESET}{f.LIGHTRED_EX}]{f.RESET} {f.GREEN}->{f.RESET} {f.LIGHTGREEN_EX}Join Stats Cleared{f.RESET}")

	@called_once_a_day_at_midnight.before_loop
	async def before(self):
		await self.bot.wait_until_ready()
		print(f"{f.LIGHTRED_EX}[{f.RESET}{f.BLUE}(Loop Created){f.RESET}{f.LIGHTRED_EX}]{f.RESET} {f.GREEN}->{f.RESET} {f.LIGHTGREEN_EX}Join Stat Loop{f.RESET}")


	@tasks.loop(seconds=1)
	async def called_once_a_week(self):
		await asyncio.sleep(secs_till_week()())
		del self.weekJoins
		del self.weekMsgs
		print(f"{f.LIGHTRED_EX}[{f.RESET}{f.BLUE}(Loop Triggered){f.RESET}{f.LIGHTRED_EX}]{f.RESET} {f.GREEN}->{f.RESET} {f.LIGHTGREEN_EX}Join Week Stats Cleared{f.RESET}")

	@called_once_a_week.before_loop
	async def before(self):
		await self.bot.wait_until_ready()
		print(f"{f.LIGHTRED_EX}[{f.RESET}{f.BLUE}(Loop Created){f.RESET}{f.LIGHTRED_EX}]{f.RESET} {f.GREEN}->{f.RESET} {f.LIGHTGREEN_EX}Join Week Stat Loop{f.RESET}")

	@commands.command(name='membercount', aliases=['mc'], description="shows member statistics for the guild", usage='Send Messages', help="```Example: ;mc```")
	async def membercount(self, ctx):
		guild=ctx.guild
		try:
			joins=self.joins[guild.id]
		except:
			joins=0
		if joins >= 0:
			joins=f"+{joins}"
		return await ctx.send(embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)).add_field(name=f"Users({joins})", value=str(len([m for m in ctx.guild.members])), inline=True).add_field(name="Humans", value=str(len([m for m in ctx.guild.members if not m.bot])), inline=True).add_field(name="Bots", value=str(len([m for m in ctx.guild.members if m.bot])), inline=True).set_author(name=guild.name, icon_url=guild.icon))



async def setup(client): 
   await client.add_cog(membercounts(client))