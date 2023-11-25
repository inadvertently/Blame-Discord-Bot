import motor.motor_asyncio, datetime, asyncio, aiohttp, requests, difflib, typing
import discord,io,os,sys,json,datetime,functools
from discord.ext import commands
from Core import utils as util
from PIL import Image
import http
from urllib.request import urlopen
from io import BytesIO
import base64
def num(number):
	return ("{:,}".format(number))

class LookupS(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.db = self.bot.db["guildAuth"]
		self.errorcol = 0xA90F25 # error color
		self.urgecolor = 0xF3DD6C # exclamation color
		self.error=discord.Colour.blurple()
		self.success = discord.Colour.blurple() #theme
		self.session=aiohttp.ClientSession()
		self.checkmoji = "<:blurple_check:921544108252741723>" # success emoji
		self.xmoji = "<:yy_yno:921559254677200957>" # unsuccessful emoji
		self.urgentmoji = "<:n_:921559211366838282>" # exclamation emoji

	@commands.command(name='xbox', description="show a xbox account", brief='username', usage='Send Messages', help="```Example: ;xbox cop```")
	async def xbox(self, ctx, *, username=None):
		async with ctx.typing():
			try:
				try:
					username=username.replace(" ", "%20")
				except:
					pass
				async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
					async with client.get(f"https://playerdb.co/api/player/xbox/{username}") as r:
						data = await r.json()
						try:
							embed=discord.Embed(title=data['data']['player']['username'], color=int("0f7c0f", 16), url=f"https://xboxgamertag.com/search/{username}").add_field(name='Gamerscore', value=data['data']['player']['meta']['gamerscore'], inline=True).add_field(name='Tenure', value=data['data']['player']['meta']['tenureLevel'], inline=True).add_field(name='Tier', value=data['data']['player']['meta']['accountTier'], inline=True).add_field(name='Rep', value=data['data']['player']['meta']['xboxOneRep'].strip("Player"), inline=True).set_author(name=ctx.author, icon_url=ctx.author.display_avatar).set_footer(text="Xbox", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/1024px-Xbox_one_logo.svg.png").add_field(name='Color', value=f"#{requests.get(data['data']['player']['meta']['preferredColor']).json()['primaryColor']}", inline=True)
							embed.set_thumbnail(url=data['data']['player']['avatar']).add_field(name="ID", value=data['data']['player']['id'], inline=True)
							if data['data']['player']['meta']['bio']:
								embed.description=data['data']['player']['meta']['bio']
							await ctx.reply(embed=embed)
						except:
							embed=discord.Embed(title=data['data']['player']['username'], color=int("0f7c0f", 16), url=f"https://xboxgamertag.com/search/{username}").add_field(name='Gamerscore', value=data['data']['player']['meta']['gamerscore'], inline=True).add_field(name='Tenure', value=data['data']['player']['meta']['tenureLevel'], inline=True).add_field(name='Tier', value=data['data']['player']['meta']['accountTier'], inline=True).add_field(name='Rep', value=data['data']['player']['meta']['xboxOneRep'].strip("Player"), inline=True).set_author(name=ctx.author, icon_url=ctx.author.display_avatar).set_footer(text="Xbox", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/1024px-Xbox_one_logo.svg.png").add_field(name='Color', value=f"#{requests.get(data['data']['player']['meta']['preferredColor']).json()['primaryColor']}", inline=True).add_field(name="ID", value=data['data']['player']['id'], inline=True)
							if data['data']['player']['meta']['bio']:
								embed.description=data['data']['player']['meta']['bio']
							await ctx.reply(embed=embed)
			except:
				return await ctx.send(embed=discord.Embed(description=f"{self.urgentmoji} {ctx.author.mention}: **Gamertag `{username}` not found**", color=int("faa61a", 16)))

	def crop_skin(self, raw_img):
		img = Image.open(raw_img)
		# coords of the face in the skin
		cropped = img.crop((8, 8, 16, 16))
		resized = cropped.resize((500, 500), resample=Image.NEAREST)

		output = io.BytesIO()
		resized.save(output, format="png")
		output.seek(0)

		return output
		
	@commands.command(name="minecraft", description="Shows information about a Minecraft user", brief="username", aliases=["namemc"], usage='Send Messages',help="```Example: ;namemc cop```")
	async def minecraft(self, ctx, *, user):
		async with self.session.get(f"https://api.mojang.com/users/profiles/minecraft/{user}") as resp:
			if resp.status != 200:
				return await ctx.send("Could not find user. Sorry")
			data = await resp.json()
		name = data["name"]
		uuid = data["id"]
		url=f"https://namemc.com/{name}?q={uuid}"

		async with self.session.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}") as resp:
			if resp.status != 200:
				return await ctx.send("An error occurred while fetching profile data from Mojang. Sorry.")
			profile_data = await resp.json()
		raw_texture_data = profile_data["properties"][0]["value"]
		texture_data = json.loads(base64.b64decode(raw_texture_data))
		async with self.session.get(texture_data["textures"]["SKIN"]["url"]) as resp:
			if resp.status != 200:
				return await ctx.send("An error occurred while fetching skin data from Mojang. Sorry.")
			bytes = await resp.read()
			img = io.BytesIO(bytes)

		# Crop out only the face of the skin
		partial = functools.partial(self.crop_skin, img)
		face = await self.bot.loop.run_in_executor(None, partial)

		em = discord.Embed(
			title=name,url=url,
			color=0x70B237,
		)
		em.set_thumbnail(url="attachment://face.png")
		em.set_footer(text=f"UUID: {uuid}")

		em.add_field(name="Previous Names", value="N/A")

		file = discord.File(face, filename="face.png")
		await ctx.send(embed=em, file=file)


	@commands.command(name='github', description='show github account information', usage='Send Messages', help="```Example: ;github antinuke0day```", brief='username')
	async def github(self, ctx, user):
		try:
			def user_data():
				url = f"https://api.github.com/users/{user}"
				
				response = urlopen(url)
				data = json.loads(response.read())

				with open(f"db/{ctx.message.guild.id}.json", "w") as f:
					json.dump(data, f, indent=4)

			user_data()

			with open(f"db/{ctx.message.guild.id}.json", "r") as f:
				data = json.load(f)

				bio = data["bio"]
				avatar = data["avatar_url"]
				followers = str(data["followers"])
				following = str(data["following"])
				twitter = data["twitter_username"]
				email = data["email"]
				company = data["company"]
				if data["blog"] == "":
					blog = "None"
				else:
					blog = data["blog"]
			
			repos = data["repos_url"]
			response = urlopen(repos)
			data = json.loads(response.read())
			url = f"https://github.com/{user}"
			git = self.bot.get_emoji(921613260720074773)
			bi = self.bot.get_emoji(921796465544822784)
			mut = self.bot.get_emoji(921796523182919780)
			folmut = self.bot.get_emoji(921796458510946374)
			twit = self.bot.get_emoji(921807071970729984)
			mail = self.bot.get_emoji(921838079118028800)
			blow = self.bot.get_emoji(921574528163938325)
			glo = self.bot.get_emoji(921613254168547388)
			tab = self.bot.get_emoji(921753792641392690)
			url2 = f"https://github.com/{user}?tab=following"
			url3 = f"https://github.com/{user}?tab=followers"
			url4 = f"https://github.com/{user}?tab=repositories"
			url5 = f"https://twitter.com/{twitter}"

			embed = discord.Embed(title=f"GitHub Search {git}", description=f"[{user}]({url})", colour=discord.Color.blurple())
			embed.set_thumbnail(url=avatar)
			embed.add_field(name=f"{bi} __Bio__", value=f'{bio}')
			embed.add_field(name=f"{mut} __Followers__", value=f'[{followers}]({url3})')
			embed.add_field(name=f"{folmut} __Following__", value=f'[{following}]({url2})')
			embed.add_field(name="__Socials__", value=f"{twit} **Twitter:** [{twitter}]({url5})\n{mail} **Email:** {email}\n{blow} **Blog:** {blog}\n{glo} **Company** {company}\n{tab} **Repositories:** [{(len(data))}]({url4})")

			await ctx.send(embed=embed)
		except Exception as e:
			print(e)

	@commands.command(name='wanted', description="wanted poster of a member's avatar", usage='Send Messages', help="```Example: ;wanted @cop#0001```", brief="member")
	async def wanted(self, ctx, user: discord.Member = None):
		if user == None:
			user = ctx.author
		wanted = Image.open("assets/wanted.jpg")
		print("jje")

		asset = user.display_avatar.with_size(128)
		data = BytesIO(await asset.read())
		pfp = Image.open(data)

		pfp = pfp.resize((177,177))

		wanted.paste(pfp, (120,212))

		wanted.save("assets/profile.jpg")

		await ctx.send(file = discord.File("assets/profile.jpg"))

	@commands.command(name='rip', description="rips a member's avatar", usage="Send Messages", help="```Example: ;rip @cop#0001```", brief="member")
	async def rip(self, ctx, user: discord.Member = None):
		if user == None:
			user = ctx.author
		rip = Image.open("assets/rip.png")

		asset = user.display_avatar.with_size(128)
		data = BytesIO(await asset.read())
		pfp = Image.open(data)

		pfp = pfp.resize((177,177))

		rip.paste(pfp, (120,250))

		rip.save("assets/profile2.png")

		await ctx.send(file = discord.File("assets/profile2.png"))

	@commands.command(name='burn', description="burn a member's avatar", usage='Send Messages', help="```Example: ;burn @cop#0001```", brief="member")
	async def burn(self, ctx, user: discord.Member = None):
		if user == None:
			user = ctx.author
		burn = Image.open("assets/burn.gif")

		asset = user.display_avatar.with_size(128)
		data = BytesIO(await asset.read())
		pfp = Image.open(data)


		pfp = pfp.resize((140,140))

		burn.paste(pfp, (130,130))

		burn.save("assets/burn2.gif", save_all=True)

		await ctx.send(file = discord.File("assets/burn2.gif"))

	@commands.command(name='triggered', description="shows a member's avatar as triggered", help="```Example: ;triggered @cop#0001```", brief="member", usage='Send Messages')
	async def triggered(self, ctx, member: discord.Member=None):
		if not member: # if no member is mentioned
			member = ctx.author # the user who ran the command will be the member
			
		async with aiohttp.ClientSession() as trigSession:
			async with trigSession.get(f'https://some-random-api.ml/canvas/triggered?avatar={member.display_avatar.with_size(1024)}') as trigImg: # get users avatar as png with 1024 size
				imageData = BytesIO(await trigImg.read()) # read the image/bytes
				
				await trigSession.close() # closing the session and;
				
				await ctx.reply(file=discord.File(imageData, 'triggered.gif'))


	@commands.command(name='blame', description="blameify a member's avatar", brief='member', usage='Send Messages', help="```Example: ;blame @cop#0001```",aliases = ['blameify'])
	async def blame(self, ctx, member: discord.Member = None):
		member = member or ctx.author
		async with ctx.typing():
			async with aiohttp.ClientSession() as session:
				async with session.get(
				f'https://some-random-api.ml/canvas/blurple?avatar={member.display_avatar.replace(static_format="png")}'
			) as af:
					if 300 > af.status >= 200:
						fp = BytesIO(await af.read())
						file = discord.File(fp, "blurple.png")
						em = discord.Embed(
							color=discord.Color.blurple(),
						)
						em.set_image(url="attachment://blurple.png")
						await ctx.send(embed=em, file=file)
					else:
						await ctx.send('I failed... Sorry')
					await session.close()

	@commands.command(name='lgbtq', description="lgbtqify a member's avatar", usage='Send Messages', brief='member', help="```Example: ;lgbtq @sorrow#1984```")
	async def lgbtq(self, ctx, member: discord.Member = None):
		member = member or ctx.author
		async with ctx.typing():
			async with aiohttp.ClientSession() as session:
				async with session.get(
				f'https://some-random-api.ml/canvas/gay?avatar={member.display_avatar.with_size(128).with_static_format("png")}'
			) as af:
					if 300 > af.status >= 200:
						fp = BytesIO(await af.read())
						file = discord.File(fp, "gay.png")
						em = discord.Embed(
							color=discord.Color.blurple(),
						)
						em.set_image(url="attachment://gay.png")
						await ctx.send(embed=em, file=file)
					else:
						await ctx.send('No horny :(')
					await session.close()


async def setup(bot):
	await bot.add_cog(LookupS(bot))