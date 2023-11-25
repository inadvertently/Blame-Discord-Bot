import discord, motor, typing, re, aiohttp, io
from discord.ext import commands
import Core.exceptions as exceptions
import Core.utils as utils, math, asyncio
from libraries import emoji_literals
from Core.utils import get_theme

def remove_mentions(text):
	"""Remove mentions from string"""
	return (re.sub(r"<@\!?[0-9]+>", "", text)).strip()

class LastFm(commands.Cog):
	"""LastFM commands"""

	def __init__(self, bot):
		self.bot = bot
		self.icon = "🎵"
		self.db = self.bot.db["lastfm"] #fetching collection 1
		self.reactiondb = self.bot.db["lastfmReactions"]
		self.cache = {}
		self.cover_base_urls = [
			"https://lastfm.freetls.fastly.net/i/u/34s/{0}",
			"https://lastfm.freetls.fastly.net/i/u/64s/{0}",
			"https://lastfm.freetls.fastly.net/i/u/174s/{0}",
			"https://lastfm.freetls.fastly.net/i/u/300x300/{0}",
			"https://lastfm.freetls.fastly.net/i/u/{0}",
		]

	@commands.group(aliases = ['lf'])
	async def lastfm(self, ctx):
		try:
			if ctx.invoked_subcommand is None:
				embed = discord.Embed(title="Command: lastfm", description="Get your lastfm data\n```Syntax: lastfm [subcommand] <argument>\nExample: lastfm set jac1337```", color = discord.Color.blurple())
				embed.set_author(name="LastFM help", icon_url=ctx.me.avatar.url)
				embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('lastfm').walk_commands()])} ・ LastFM")
				return await ctx.send(embed=embed)
		except Exception as e:
			print(e)

	@lastfm.command(
		aliases = ['prof'],
		usage = 'Send_messages',
		description = 'View yours or another members lastfm profile',
		brief = 'member',
		help = "```Usage: lastfm [subcommand] <member>\nExample: lastfm profile @jac#1337```"
	)
	async def profile(self, ctx, user: discord.User=None):
		async with ctx.typing():
			if user == None:
				user = ctx.author
			existing = await utils.index_user(self, bot=self.bot, author=user.id)
			if existing is None:
				return await ctx.send(f"No Lastfm account has been set for, **{user}**")
			"""See your Last.fm profile"""
			message = await ctx.send(embed=await utils.get_userinfo_embed(self, username=existing))
			voting = await self.reactiondb.find_one({"user_id": user.id})
			if voting:
				if voting['upvote'].startswith("<"): 
					await message.add_reaction(voting['upvote'])
				else:
					await message.add_reaction(emoji_literals.NAME_TO_UNICODE.get(voting['upvote']))
				if voting['downvote'].startswith("<"): 
					await message.add_reaction(voting['downvote'])
				else:
					await message.add_reaction(emoji_literals.NAME_TO_UNICODE.get(voting['downvote']))

	@lastfm.command(
		aliases = ['np'],
		usage = 'Send_messages',
		description = "See what you're playing on lastfm",
		brief = 'member',
		help = "```Usage: lastfm [subcommand] <member>\nExample: lastfm nowplaying @jac#1337```"
		)
	async def nowplaying(self, ctx, user: discord.User=None):
			async with ctx.typing():
				if user == None:
					user = ctx.author
				existing = await utils.index_user(self, bot=self.bot, author=user.id)
				if existing is None:
					return await ctx.send(f'No Lastfm account has been set for, **{user}**')
				message = await ctx.send(embed = await utils.now_playing(self, username=existing, avatar=user.display_avatar.url))
				voting = await self.reactiondb.find_one({"user_id": user.id})
				if voting:
					if voting['upvote'].startswith("<"): 
						await message.add_reaction(voting['upvote'])
					else:
						await message.add_reaction(emoji_literals.NAME_TO_UNICODE.get(voting['upvote']))
					if voting['downvote'].startswith("<"): 
						await message.add_reaction(voting['downvote'])
					else:
						await message.add_reaction(emoji_literals.NAME_TO_UNICODE.get(voting['downvote']))
	@lastfm.command(
		aliases = ['yt'],
		usage = 'send_messages', 
		description = 'Fetch your now playing song on youtube',
		brief = 'member',
		help = '```Example: lf youtube```'
	)
	async def youtube(self, ctx, user: discord.User=None):
		async with ctx.typing():
			if user == None:
				user = ctx.author
			existing = await utils.index_user(self, bot=self.bot, author=user.id)
			if existing is None:
				return await ctx.send(f'No Lastfm account has been set for, **{user}**')
			try:
				await ctx.reply(await utils.scrape_np_to_yt(self, username=existing))
			except:
				return await utils.send_issue(ctx, "No results found..")

	@lastfm.command(
		aliases = ['cv'],
		usage = 'send_messages',
		description = 'Fetch the cover for your currently playing song',
		brief = 'member',
		help = '```Example: lf cover```'
	)
	async def cover(self, ctx, user: discord.User=None):
		async with ctx.typing():
			if user == None:
				user = ctx.author
			existing = await utils.index_user(self, bot=self.bot, author=user.id)
			if existing:
				data = await utils.api_req(self, params=
					{"user": existing, "method": "user.getrecenttracks", "limit": 1}
				)
				image_url = data["recenttracks"]["track"][0]["image"][-1]["#text"]
				image_hash = image_url.split("/")[-1].split(".")[0]
				big_image_url = self.cover_base_urls[4].format(image_hash)
				artist_name = data["recenttracks"]["track"][0]["artist"]["#text"]
				album_name = data["recenttracks"]["track"][0]["album"]["#text"]
				async with aiohttp.ClientSession() as session:	
					async with session.get(big_image_url) as response:
						buffer = io.BytesIO(await response.read())
						return await ctx.reply(
							file=discord.File(fp=buffer, filename=image_hash + ".jpg"),
							embed = await utils.now_playing3(self, username=existing, avatar=user.display_avatar.url)
						)



		

	@lastfm.command(
		aliases = ['react', 'reactions','emojis','emoji'],
		usage = "Send_messages",
		description = "Set a custom upvote and downvote for your lastfm nowplaying",
		brief = "upvote, downvote",
		help = "```Syntax: lastfm reactions <upvote> <downvote>\nExample: lastfm reactions 👍 👎 "
	)
	async def reaction(self, ctx, emoji1, emoji2):
		if not emoji1 and not emoji2:
			return await utils.send_command_help(ctx)
		if emoji1 and emoji2:
			if emoji1.startswith("<"):
				emoji1=str(emoji1)
			else:
				emoji1=emoji_literals.UNICODE_TO_NAME.get(emoji1)
			if emoji2.startswith("<"):
				emoji2=str(emoji2)
			else:
				emoji2=emoji_literals.UNICODE_TO_NAME.get(emoji2)
			check = await self.reactiondb.find_one({"user_id": ctx.author.id})
			if check:
				await self.reactiondb.update_one({"user_id": ctx.author.id}, {"$set": {"upvote": str(emoji1)}})
				await self.reactiondb.update_one({"user_id": ctx.author.id}, {"$set": {"downvote": str(emoji2)}})
				embed2 = discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} **upvote** changed to {emoji1} **downvote** changed to {emoji2}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
				return await ctx.send(embed=embed2)
			else:
				await self.reactiondb.insert_one({
				"user_id": ctx.author.id,
				"upvote": str(emoji1),
				"downvote": str(emoji2)
				})
				embed = discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} **upvote** set to {emoji1} **downvote** set to {emoji2}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
				return await ctx.send(embed=embed)
		else:
			return await ctx.send(f"{ctx.author.mention} An **invalid** emoji was given, please make the emotes being given are from a mutual guild.")


	@commands.command(
		aliases= ['np'],
		usage = 'Send_messages',
		description = "See what you're playing on lastfm",
		brief = 'member',
		help = "```Usage: fm <member>\nExample: fm @jac#1337```"
		)
	async def fm(self, ctx, user: discord.User=None):
		async with ctx.typing():
			if user == None:
				user = ctx.author
			existing = await utils.index_user(self, bot=self.bot, author=user.id)
			if existing is None:
				return await ctx.send(f'No Lastfm account has been set for, **{user}**')
			message = await ctx.send(embed = await utils.now_playing(self, username=existing, avatar=user.display_avatar.url))
			voting = await self.reactiondb.find_one({"user_id": user.id})
			if voting:
				if voting['upvote'].startswith("<"): 
					await message.add_reaction(voting['upvote'])
				else:
					await message.add_reaction(emoji_literals.NAME_TO_UNICODE.get(voting['upvote']))
				if voting['downvote'].startswith("<"): 
					await message.add_reaction(voting['downvote'])
				else:
					await message.add_reaction(emoji_literals.NAME_TO_UNICODE.get(voting['downvote']))

	
   # @lastfm.command()
   # async def topartists(self, ctx, user: discord.User=None):
	 #   async with ctx.typing():
		  #  if user == None:
			  #  user = ctx.author
		  #  existing = await utils.index_user(self, bot=self.bot, author=user.id)
		  #  if existing is None:
				#return await ctx.send(f'No Lastfm account has been set for, **{user}**')
		   # await ctx.send(embed = await utils.topartists(self, username=await utils.index_user(self, author=user.id), avatar=user.display_avatar.url))


	@lastfm.command(
		aliases = ['login'],
		usage = 'Send_messages',
		description = "Login to your Lastfm account",
		brief = 'member',
		help = "```Usage: lastfm [subcommand] <member>\nExample: lastfm set sorrow1984```"
		)
	async def set(self, ctx, username):
		check = await self.db.find_one({"user_id": ctx.author.id})
		if not check:
			search = await utils.get_userinfo_embed(self, username)
			if search is None:
				return await utils.send_issue(ctx, "The username **{username}** was not found..")
			else:
				await self.db.insert_one({
					"user_id": ctx.author.id,
					"lastfm_username": f"{username}"})
				await utils.send_blurple(ctx, f"{ctx.author.mention}, your **Last.fm** username has been set to ``{username}`` ")
		else:
			return await ctx.send(f"{ctx.author.mention}, you already have a **LastFM username on file** please use ``lf unset`` if you'd like to remove it.")

	@lastfm.command(
		aliases = ['logout'],
		usage = 'Send_messages',
		description = "Logout of your lastfm account",
		brief = 'member',
		help = "```Usage: lastfm [subcommand] <member>\nExample: lastfm unset```"
		)
	async def unset(self, ctx):
		check = await self.db.find_one({"user_id": ctx.author.id})
		if check:
			await self.db.delete_many({"user_id": ctx.author.id})
			return await ctx.send(f"{ctx.author.mention}, your LastFM username has been unset")
		else:
			return await ctx.send("There is no lastfm data for you. Please use ``lf set``")


	#@lastfm.command()
   # async def milestone(self, ctx, n: int, user: discord.User=None):
		return
		if user == None:
			user = ctx.author
		async with ctx.typing():
			"""See what your n:th scrobble was"""
			existing = await utils.index_user(self, bot=self.bot, author=user.id)
			if existing is None:
				return await ctx.send(f'No Lastfm account has been set for, **{user}**')
			else:
				n_display = utils.ordinal(n)
				if n < 1:
					raise exceptions.CommandWarning(
						"Please give a number between 1 and your total amount of listened tracks."
					)
				per_page = 100
				pre_data = await utils.api_req(self, params=
					{"user": await utils.index_user(self, author=user.id), "method": "user.getrecenttracks", "limit": per_page}
				)
				total = int(pre_data["recenttracks"]["@attr"]["total"])
				if n > total:
					raise exceptions.CommandWarning(
						f"You have only listened to **{total}** tracks! Unable to show {n_display} track"
					)

				remainder = total % per_page
				total_pages = int(pre_data["recenttracks"]["@attr"]["totalPages"])
				if n > remainder:
					n = n - remainder
					containing_page = total_pages - math.ceil(n / per_page)
				else:
					containing_page = total_pages

				final_data = await utils.api_req(self, params=
					{
						"user": await utils.index_user(self, author=user.id),
						"method": "user.getrecenttracks",
						"limit": per_page,
						"page": containing_page,
					}
				)

				# if user is playing something, the current nowplaying song will be appended to the list at index 101
				# cap to 100 first items after reversing to remove it
				tracks = list(reversed(final_data["recenttracks"]["track"]))[:100]
				nth_track = tracks[(n % 100) - 1]
				await ctx.send(
					f"**{user}'s** {n_display} scrobble was ***{nth_track['name']}*** by **{nth_track['artist']['#text']}**"
				)


	@lastfm.command(
		aliases=["ta"],
		usage = 'Send_messages',
		description = "See what your topartists on LastFM",
		brief = 'member',
		help = "```Usage: lastfm [subcommand] <member>\nExample: lastfm topartists @jac#1337```"
		)
	async def topartists(self, ctx, user: discord.User=None):
		"""See your most listened to artists"""
		async with ctx.typing():
			try:
				if user == None:
					user = ctx.author
				existing = await utils.index_user(self, bot=self.bot, author=user.id)
				if existing is None:
					return await ctx.send(f'No Lastfm account has been set for, **{user}**')
				else:

					data = await utils.api_req(self, params=
							{
								"user": existing,
								"method": "user.gettopartists",
								"limit": 10,
							}
						)
				user_attr = data["topartists"]["@attr"]
				artists = data["topartists"]["artist"][: 10]

				if not artists:
					raise exceptions.CommandInfo("You have not listened to anything yet!")

				rows = []
				for i, artist in enumerate(artists, start=1):
					name = discord.utils.escape_markdown(artist["name"])
					plays = artist["playcount"]
					rows.append(f"`#{i:2}` **{name}** -- **({plays})** {utils.format_plays(plays)}")

				#image_url = artists[0]["name"]
				#formatted_timeframe = humanized_period(arguments["period"]).capitalize()


				try:
					color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)
				except:
					color = discord.Color.blurple()
				content = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
				#content.colour = await self.cached_image_color(image_url)
				content.set_thumbnail(url=user.display_avatar.url)
				#content.set_footer(text=f"Top unique artists: {user_attr['total']}")
				content.set_author(
					name=f"{user}'s — All time top artist's",
					icon_url=user.display_avatar.url,
				)

				await utils.send_as_pages(ctx, content, rows, 10)
			except Exception as e:
				print(e)

	@lastfm.command(
		aliases=["talb", 'tab'],
		usage = 'Send_messages',
		description = "View your topalbums on LastFM",
		brief = 'member',
		help = "```Usage: lastfm [subcommand] <member>\nExample: lastfm topalbums @jac#1337```"
		)
	async def topalbums(self, ctx, user: discord.User=None):
		async with ctx.typing():
			if user == None:
				user = ctx.author
			existing = await utils.index_user(self, bot=self.bot, author=user.id)
			if existing is None:
				return await ctx.send(f'No Lastfm account has been set for, **{user}**')
			else:
				data = await utils.api_req(self, params=
					{
						"user": existing,
						"method": "user.gettopalbums",
						"limit": 10,
					}
				)
			user_attr = data["topalbums"]["@attr"]
			albums = data["topalbums"]["album"][: 10]

			if not albums:
				raise exceptions.CommandInfo("You have not listened to anything yet!")

			rows = []
			for i, album in enumerate(albums, start=1):
				name = discord.utils.escape_markdown(album["name"])
				artist_name = discord.utils.escape_markdown(album["artist"]["name"])
				plays = album["playcount"]
				rows.append(
					f"`#{i:2}` ***{name}*** by: {artist_name} **({plays})** {utils.format_plays(plays)} "
				)

			image_url = albums[0]["image"][-1]["#text"]
			#formatted_timeframe = humanized_period(arguments["period"]).capitalize()
			try:
				color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)
			except:
				color = discord.Color.blurple()
			content = discord.Embed(color=color)
			#content.colour = await self.cached_image_color(image_url)
			content.set_thumbnail(url=image_url)
			#content.set_footer(text=f"Total unique albums: {user_attr['total']}")
			content.set_author(
				name=f"{user}'s — All time top album's",
				icon_url=user.display_avatar.url,
			)

			await utils.send_as_pages(ctx, content, rows, 10)

	@lastfm.command(
		aliases=["tt"],
		usage = 'Send_messages',
		description = "View your toptracks using LastFM",
		brief = 'member',
		help = "```Usage: lastfm [subcommand] <member>\nExample: lastfm toptracks @jac#1337```"
		)
	async def toptracks(self, ctx, user: discord.User=None):
		"""See your most listened to tracks"""
		async with ctx.typing():
			if user == None:
				user = ctx.author
			existing = await utils.index_user(self, bot=self.bot, author=user.id)
			if existing is None:
				return await ctx.send(f'No Lastfm account has been set for, **{user}**')
			else:
				data = await utils.api_req(self, params=
					{
						"user": existing,
						"method": "user.gettoptracks",
						"limit": 10,
					}
				)
			user_attr = data["toptracks"]["@attr"]
			tracks = data["toptracks"]["track"][: 10]

			if not tracks:
				raise exceptions.CommandInfo("You have not listened to anything yet!")

			rows = []
			for i, track in enumerate(tracks, start=1):
				#if i == 1:
					#image_url = await self.get_artist_image(tracks[0]["artist"]["name"])

				name = discord.utils.escape_markdown(track["name"])
				artist_name = discord.utils.escape_markdown(track["artist"]["name"])
				plays = track["playcount"]
				rows.append(
					f"`#{i:2}` ***{name}*** by **{artist_name}** (**{plays}**) {utils.format_plays(plays)}"
				)

			#formatted_timeframe = humanized_period(arguments["period"]).capitalize()
			try:
				color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)
			except:
				color = discord.Color.blurple()
			content = discord.Embed(color=color)
			#content.colour = await self.cached_image_color(image_url)
			content.set_thumbnail(url=user.display_avatar.url)
		   # content.set_footer(text=f"Total unique tracks: {user_attr['total']}")
			content.set_author(
				name=f"{user}'s — All time top tracks",
				icon_url=user.display_avatar.url,
			)

			await utils.send_as_pages(ctx, content, rows, 15)

	@lastfm.command(
		aliases=["recents", "re", 'latest', 'last', 'rec'],
		usage = 'Send_messages',
		description = "View the last songs you played using LastFm",
		brief = 'member',
		help = "```Usage: lastfm [subcommand] <member>\nExample: lastfm recent @jac#1337```"
		)
	async def recent(self, ctx, user: discord.User=None):
		"""Get your recently listened to tracks"""
		async with ctx.typing():
			if user == None:
				user = ctx.author
			existing = await utils.index_user(self, bot=self.bot, author=user.id)
			if existing is None:
				return await ctx.send(f'No Lastfm account has been set for, **{user}**')
			else:

				data = await utils.api_req(self, params=
					{"user": await utils.index_user(self, bot=self.bot, author=user.id), "method": "user.getrecenttracks", "limit": 10}
				)
				user_attr = data["recenttracks"]["@attr"]
				tracks = data["recenttracks"]["track"][:10]

				if not tracks:
					raise exceptions.CommandInfo("You have not listened to anything yet!")

				rows = []
				for track in tracks:
					name = discord.utils.escape_markdown(track["name"])
					artist_name = discord.utils.escape_markdown(track["artist"]["#text"])
					rows.append(f"***{name}*** by **{artist_name}** ")

				image_url = tracks[0]["image"][-1]["#text"]
				try:
					color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)
				except:
					color = discord.Color.blurple()
				content = discord.Embed(color=color)
				#content.colour = await self.cached_image_color(image_url)
				content.set_thumbnail(url=image_url)
				#content.set_footer(text=f"Total scrobbles: {user_attr['total']}")
				content.set_author(
					name=f"{user}'s — recent tracks",
					icon_url=user.display_avatar.url,
				)

				await utils.send_as_pages(ctx, content, rows, 15)


   # async def server_lastfm_usernames(self, ctx):
	   # guild_user_ids = [user.id for user in ctx.guild.members]
	   # ids = []
		#data = self.db.find({"user_id": { "$in": guild_user_ids}})
		#async for user in data:
			#ids.append(user['user_id'])
	async def get_playcount(self, artist, username, reference=None):
		data = await utils.api_req(self, params=
			{
				"method": "artist.getinfo",
				"user": username,
				"artist": artist,
				"autocorrect": 1,
			}
		)
		try:
			count = int(data["artist"]["stats"]["userplaycount"])
		except (KeyError, TypeError):
			count = 0

		name = data["artist"]["name"]

		if reference is None:
			return count
		return count, reference, name

	async def server_lastfm_usernames(self, ctx):
		ids= []
		guild_user_ids = [user.id for user in ctx.guild.members]
		cursor = self.db.find({"user_id": { "$in": guild_user_ids}})
		async for doc in cursor:
			ids.append(doc['user_id'])
			resp = list(ids)
		return resp

	@lastfm.command(
		aliases=["wk", "whomstknows"],
		usage = 'send_messages',
		description = 'Find out who knows the specified artist the most!',
		brief = 'artist',
		help = "```Syntax: lf whoknows [artist]\nExample: lf whoknows tems```"
		)
	@commands.guild_only()
	async def whoknows(self, ctx, *, artistname=None):
		async with ctx.typing():
			try:
				if artistname == None:
					artistname = (await utils.getnowplaying2(self, username=await utils.index_user(self, bot=self.bot, author=ctx.author.id)))

				listeners = []
				tasks = []
				for user_id, lastfm_username in await utils.server_lastfm_usernames(self, ctx=ctx):
					member = ctx.guild.get_member(user_id)
					if member is None:
						continue

					tasks.append(self.get_playcount(artistname, lastfm_username, member))

				if tasks:
					data = await asyncio.gather(*tasks)
					for playcount, member, name in data:
						artistname = name
						if playcount > 0:
							listeners.append((playcount, member))
				else:
					return await utils.send_error(ctx, f"LastFM accounts have not been set in this server!")

				artistname = discord.utils.escape_markdown(artistname)

				rows = []
				total = 0
				content = discord.Embed(title =f"Top listeners for __{artistname}__", description="", url=f"https://www.last.fm/user/{lastfm_username}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
				for i, (playcount, member) in enumerate(
					sorted(listeners, key=lambda p: p[0], reverse=True), start=1
				):
					if i == 1:
						rank = '<a:crown_DIOR:1019781942243241994>'
					else:
						rank = f"`{i:1}.`"
					rows.append(
						f"{rank} **[{utils.displayname(member)}](https://www.last.fm/user/{lastfm_username})** with **{playcount:,}** {utils.format_plays(playcount)}"
					)
					total += playcount
				content.set_author(name=f"{ctx.author} ({len(rows)} entries)", icon_url=ctx.author.display_avatar)
				content.set_footer(text=f"Displaying (1/10) entries", icon_url=ctx.author.display_avatar.url)
				await utils.send_as_page(ctx, content, rows)
				if not rows:
					return await utils.send_error(ctx, f"LastFM accounts have not been set in this server!")
			except Exception as e:
				print(e)
			

async def setup(bot):
	await bot.add_cog(LastFm(bot))