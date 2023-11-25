import discord, random, aiohttp, httpx, Core.utils as util
from discord.ext import commands
from typing import List
import discord.ui
from serpapi import GoogleSearch


class Paginator(discord.ui.View):
	def __init__(self, embeds: List[discord.Embed]):
		super().__init__(timeout=60)
		self.embeds = embeds
		self.current_page = 0

	@discord.ui.button(label="⬅️", style=discord.ButtonStyle.blurple, disabled=True)
	async def previous_page(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.current_page == 1:
			self.previous_page.disabled = True
		self.next_page.disabled = False
		self.current_page -= 1
		embed = self.embeds[self.current_page]

		await interaction.response.edit_message(embed=embed, view=self)

	@discord.ui.button(label="➡️", style=discord.ButtonStyle.blurple, disabled=False)
	async def next_page(self, button: discord.ui.Button, interaction: discord.Interaction):
		self.current_page += 1
		print(self.current_page)
		if self.current_page == len(self.embeds) - 1:
			self.next_page.disabled = True
		self.previous_page.disabled = False
		embed = self.embeds[self.current_page]

		await interaction.response.edit_message(embed=embed, view=self)


class memeS(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.actions = [
				'***blushes***',
				'***whispers to self***',
				'***cries***',
				'***screams***',
				'***sweats***',
				'***twerks***',
				'***runs away***',
				'***screeches***',
				'***walks away***',
				'***sees bulge***',
				'***looks at you***',
				'***notices buldge***',
				'***starts twerking***',
				'***huggles tightly***',
				'***boops your nose***',
				'***wags my tail***',
				'***pounces on you***',
				'***nuzzles your necky wecky***',
				'***unzips your pants***',
				'***licks lips***',
				'***glomps and huggles***',
				'***glomps***',
				'***looks around suspiciously***',
				'***smirks smuggly***'
				]



		self.faces = [
			"(・\`ω\´・)",
			";;w;;",
			"OwO",
			"owo",
			"UwU",
			"\>w\<",
			"^w^",
			"ÚwÚ",
			"^-^",
			":3",
			"x3",
			'Uwu',
			'uwU',
			'(uwu)',
			"(ᵘʷᵘ)",
			"(ᵘﻌᵘ)",
			"(◡ ω ◡)",
			"(◡ ꒳ ◡)",
			"(◡ w ◡)",
			"(◡ ሠ ◡)",
			"(˘ω˘)",
			"(⑅˘꒳˘)",
			"(˘ᵕ˘)",
			"(˘ሠ˘)",
			"(˘³˘)",
			"(˘ε˘)",
			"(˘˘˘)",
			"( ᴜ ω ᴜ )",
			"(„ᵕᴗᵕ„)",
			"(ㅅꈍ ˘ ꈍ)",
			"(⑅˘꒳˘)",
			"( ｡ᵘ ᵕ ᵘ ｡)",
			"( ᵘ ꒳ ᵘ ✼)",
			"( ˘ᴗ˘ )",
			"(ᵕᴗ ᵕ⁎)",
			"*:･ﾟ✧(ꈍᴗꈍ)✧･ﾟ:*",
			"*˚*(ꈍ ω ꈍ).₊̣̇.",
			"(。U ω U。)",
			"(U ᵕ U❁)",
			"(U ﹏ U)",
			"(◦ᵕ ˘ ᵕ◦)",
			"ღ(U꒳Uღ)",
			"♥(。U ω U。)",
			"– ̗̀ (ᵕ꒳ᵕ) ̖́-",
			"( ͡U ω ͡U )",
			"( ͡o ᵕ ͡o )",
			"( ͡o ꒳ ͡o )",
			"( ˊ.ᴗˋ )",
			"(ᴜ‿ᴜ✿)",
			"~(˘▾˘~)",
			"(｡ᴜ‿‿ᴜ｡)",
			]

	@commands.command(
		usage = "Send_message",
		description = "Finds and returns a random subreddit memes",
		brief = "None",
		help = "```Example: meme```"
	)
	async def meme(self, ctx):
		r = httpx.get("https://meme-api.herokuapp.com/gimme")
		res = r.json()
		title = res["title"]
		ups = res["ups"]
		author = res["author"]
		spoiler = res["spoiler"]
		nsfw = res["nsfw"]
		subreddit = res["subreddit"]
		url = res["url"]
		img = res["url"]
		postlink = res["postLink"]

		em = discord.Embed(title=f"{title}", description=f"Subreddit: **{subreddit}**\n Author: **{author}**", url=postlink)
		em.set_image(url=img)
		em.set_footer(text=f"👍 {ups}| 💬 0 | Spoiler: {spoiler} | NSFW: {nsfw}")
		return await ctx.send(embed=em)



	@commands.command(hidden=True)
	async def pagination(self, ctx: discord.ext.commands.Context):
		embeds = [
			discord.Embed(
				description="This is page 1"
			),
			discord.Embed(
				description="This is page 2"
			),
			discord.Embed(
				description="This is page 3"
			),
			discord.Embed(
				description="This is page 4"
			),
		]
		await ctx.send(embed=embeds[0], view=Paginator(embeds))


	@commands.command(aliases = ['uwuify', 'uwulock', 'uwu'])
	async def uwufy(self, ctx, *, message=None):

		if message == None:
			message = 'UwU'
		if "r" in message:
			message = message.replace("r", "w")
		if "l" in message:
			message = message.replace("l", "w")
		message = [f"{message}",
		f"**{message}**",
		f"***{message}***",
		f"**{random.choice(self.faces)}** *{message}*",
		f"*{random.choice(self.faces)}* {random.choice(self.actions)}",
		f"*{random.choice(self.faces)}* {message} ***{random.choice(self.actions)}***"
		f"**{random.choice(self.actions)}** {random.choice(self.actions)}",
		f"*{message}* {random.choice(self.actions)}",
		f"{message} *{random.choice(self.actions)}**"]
		return await ctx.send(random.choice(message))




async def setup(bot):
	await bot.add_cog(memeS(bot))