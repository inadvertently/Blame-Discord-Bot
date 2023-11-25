import discord, os, logging, json, time, random, motor, aiohttp
from discord.ext import commands, tasks
from discord.utils import get
from datetime import datetime as dt
from colorama import Fore as f
import button_paginator as pg
from Core import utils as util
from Core.utils import get_theme

def get_cmds(bot, command:str):
	exmp3 = [c.qualified_name for c in bot.get_command(command).walk_commands()]
	expm_str3 = ','.join(exmp3)
	final_data = expm_str3.replace(command, '')
	return final_data

async def format_results(ctx, bot, command: str):
	cmds = [c.qualified_name for c in bot.get_command(command).walk_commands()]
	descrips = [c.description for c in bot.get_command(command).walk_commands()]
	alias = [", ".join(c.aliases) for c in bot.get_command(command).walk_commands()]
	final = [f"**``{ctx.prefix}{cmds}`` · ``({alias})``** | *{descrips}*\n" for cmds, alias, descrips in zip(cmds, alias, descrips)]
	des = ""
	for i in final:
		des+= f"{i}"
	embed = discord.Embed(title=f"All {command} commands", description=f"**Commands:**\n{des}", color=int(await get_theme(self=bot, bot=bot, guild=ctx.guild.id), 16))
	embed.set_author(name='blame help & command overview', icon_url=ctx.me.display_avatar.url)
	embed.set_footer(text=f"{ctx.prefix}help [command] for more info on the command.")
	return embed


class Dropdown(discord.ui.Select):
	def __init__(self, ctx, bot):
		self.bot = bot
		self.ctx = ctx
		options = [
			discord.SelectOption(label='General', description='Main menu'),
			discord.SelectOption(label='Autopfp', description=f"⭐ Premium ⭐"),
			discord.SelectOption(label='Anti-Invite', description=get_cmds(bot=self.bot, command='anti-invite')),
			discord.SelectOption(label='Antiraid', description=get_cmds(bot=self.bot, command='antiraid')),
			discord.SelectOption(label='Antinuke', description="Too many.."),
			discord.SelectOption(label='Autoresponder', description=get_cmds(bot=self.bot, command='autoresponder')),
			discord.SelectOption(label='Autorole', description=get_cmds(bot=self.bot, command='autorole')),
			discord.SelectOption(label='BoostMsg', description=get_cmds(bot=self.bot, command='boostmsg')),
			discord.SelectOption(label='Boosterrole', description=get_cmds(bot=self.bot, command='boosterrole')),
			discord.SelectOption(label='FakePerms', description=get_cmds(bot=self.bot, command='fakeperms')),
			discord.SelectOption(label='Forcenick', description=get_cmds(bot=self.bot, command='forcenick')),
			discord.SelectOption(label='Game', description=get_cmds(bot=self.bot, command='game')),
			discord.SelectOption(label='Goodbye', description="Too many.."),
			discord.SelectOption(label='Joindm', description=get_cmds(bot=self.bot, command='joindm')),
			discord.SelectOption(label='Logging', description=get_cmds(bot=self.bot, command='logging')),
			discord.SelectOption(label='LastFM', description="Too many.."),
			discord.SelectOption(label='Juul', description=get_cmds(bot=self.bot, command='juul')),
			discord.SelectOption(label='Pfp', description=get_cmds(bot=self.bot, command='pfp')),
			discord.SelectOption(label='PingOnJoin', description=get_cmds(bot=self.bot, command='poj')),
			discord.SelectOption(label='React', description=get_cmds(bot=self.bot, command='react')),
			discord.SelectOption(label='ReactionRoles', description=get_cmds(bot=self.bot, command='reaction')),
			discord.SelectOption(label='Tags', description=get_cmds(bot=self.bot, command='tags')),
			#discord.SelectOption(label='Twitch Notifications', description="Too many.."),
			discord.SelectOption(label='Voicemaster', description=get_cmds(bot=self.bot, command='voice')),
			discord.SelectOption(label='Webhooks', description=get_cmds(bot=self.bot, command='webhook')),
			discord.SelectOption(label='Welcome', description="Too many..")]
		super().__init__(placeholder='General', min_values=1, max_values=1, options=options)

	async def callback(self, interaction: discord.Interaction):
		help_type = self.values[0]
		if help_type == 'General':
			general_embed = discord.Embed(color=000000).set_author(name='blame help & command overview', icon_url=self.ctx.me.display_avatar.url).set_footer(text=f"The Blame Team ・ Commands: {sum(1 for i in self.bot.walk_commands())}").add_field(name="__Top command__ ``antinuke``", value="*Set a channel that blame will autosend pfps to every  five minutes.*", inline=False).add_field(name="\n__Commands__", value="- View our commands on our **[documentation](https://docs.blame.gg) (in development)**\n- Or use the dropdown below this message to pick a category", inline=False).add_field(name="__Links__", value="[Help](https://docs.blame.gg) - [Invite the bot](https://discord.com/api/oauth2/authorize?client_id=776128410547126322&permissions=8&scope=bot) - [Support server](https://discord.gg/Xa2ZJr4atx) - [Donate](https://cash.app/$blameW)")
			await interaction.response.defer()
			await interaction.message.edit(embed=general_embed)
		else:
			await interaction.response.defer()
			await interaction.message.edit(embed=await format_results(ctx=self.ctx, bot=self.bot, command=help_type))


class DropdownView(discord.ui.View):
	def __init__(self,ctx, bot):
		self.ctx = ctx
		super().__init__()

		# Adds the dropdown to our view object.
		self.add_item(Dropdown(ctx, bot))

class MyHelp(commands.HelpCommand):
	async def send_bot_help(self, mapping):
		ctx=self.context
		bot=ctx.bot
		async with ctx.typing():
			try:
				view = DropdownView(ctx, bot)
				general_embed = discord.Embed(color=int(await get_theme(self, bot=bot, guild=ctx.guild.id), 16)).set_author(name='blame help & command overview', icon_url=ctx.me.display_avatar.url).set_footer(text=f"The Blame Team ・ Commands: {sum(1 for i in bot.walk_commands())}").add_field(name="__Top command__ ``autopfp``", value="*Set a channel that blame will autosend pfps to every  five minutes.*", inline=False).add_field(name="\n__Commands__", value="- View our commands on our **[documentation](https://docs.blame.gg) (in development)**\n- Or use the dropdown below this message to pick a category", inline=False).add_field(name="__Links__", value="[Help](https://docs.blame.gg) - [Invite the bot](https://discord.com/api/oauth2/authorize?client_id=776128410547126322&permissions=8&scope=bot) - [Support server](https://discord.gg/Xa2ZJr4atx) - [Donate](https://cash.app/$blameW)")
				return await ctx.send(embed=general_embed, view=view)

			except Exception as e:
				print(e)

	async def send_command_help(self, command):
		try:
			ctx=self.context
			bot=ctx.bot
			async with ctx.typing():
				embed = discord.Embed(title=f"Command: {command.qualified_name}", description=f"{command.description}", color=int(await get_theme(self, bot=bot, guild=ctx.guild.id), 16))
				if command.aliases:
					embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
				else:
					embed.add_field(name="Aliases", value="None")
				embed.add_field(name="⚠️ Parameters", value=command.brief)
				embed.add_field(name="🔒 Permissions", value=command.usage)
				if command.help:
					usage=command.help
					embed.add_field(name="📲 Usage", value=f"{usage}", inline=False)
				embed.set_footer(text=f"Module: {command.cog_name}.py")
				channel = self.get_destination()
				await channel.send(embed=embed)
		except Exception as e:
			print(e)


	async def send_group_help(self, group):
		ctx=self.context
		bot = ctx.bot
		async with ctx.typing():
			if isinstance(group, commands.Group):
				filtered = await self.filter_commands(group.commands, sort=False)
				tot = len(group.commands)
				print(tot)
				embedss=[]
				try:
					for i in filtered:
						try:
							for ii in i.walk_commands():
								tot+=1
						except:
							pass
				except:
					pass
				try:
					embed1 = discord.Embed(color=int(await get_theme(self, bot=bot, guild=ctx.guild.id), 16))
					embed1.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
					if group.brief:
						embedss.append(embed1)
						tot +=1
						embed1.add_field(name="⚠️ Parameters", value=group.brief)

						embed1.set_footer(text="Aliases: " + ", ".join(group.aliases)+f" ・ Module: {group.cog_name}.py ・ Entry: ({len(embedss)}/{tot} entries)")
						embed1.set_footer(text="Aliases: " + ", ".join(group.aliases)+f" ・ Module: {group.cog_name}.py ・ Entry: ({len(embedss)}/{tot} entries)")
					if group.usage:
						embed1.add_field(name="🔒 Permissions", value=group.usage)
					if group.description:
						embed1.title=f"Group Command: {group.qualified_name}"
						embed1.description=group.description
					if group.help:
						usage=group.help
						embed1.add_field(name="📲 Usage", value=f"{usage}", inline=False)
						embed1.title=f"Group Command: {group.qualified_name}"
				except Exception as e:
					print(e); pass
				for command in filtered:
					try:
						for commandd in command.walk_commands():
							emb2 = discord.Embed(color=int(await get_theme(self, bot=bot, guild=ctx.guild.id), 16))
							emb2.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
							if commandd.brief:
								embedss.append(emb2)
								emb2.add_field(name="⚠️ Parameters", value=commandd.brief)
								emb2.set_footer(text="Aliases: " + ", ".join(commandd.aliases)+f" ・ Module: {commandd.cog_name}.py ・ Entry: ({len(embedss)}/{tot} entries)")
							if commandd.usage:
								emb2.add_field(name="🔒 Permissions", value=commandd.usage)
							if commandd.description:
								emb2.title=f"Command: {commandd.qualified_name}"
								emb2.description=commandd.description
							if commandd.help:
								usage=commandd.help
								emb2.add_field(name="📲 Usage", value=f"{usage}", inline=False)
								emb2.title=f"Command: {commandd.qualified_name}"
					except:
						pass
					#tot += 1
					emb = discord.Embed(color=int(await get_theme(self, bot=bot, guild=ctx.guild.id), 16))
					emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
					if command.brief:
						embedss.append(emb)
						emb.add_field(name="⚠️ Parameters", value=command.brief)
						emb.set_footer(text="Aliases: " + ", ".join(command.aliases)+f" ・ Module: {command.cog_name}.py ・ Entry: ({len(embedss)}/{tot} entries)")
					if command.usage:
						emb.add_field(name="🔒 Permissions", value=command.usage)
					if command.description:
						emb.title=f"Command: {command.qualified_name}"
						emb.description=command.description
					if command.help:
						usage=command.help
						emb.add_field(name="📲 Usage", value=f"{usage}", inline=False)
						emb.title=f"Command: {command.qualified_name}"

				paginator = pg.Paginator(ctx.bot, embedss, ctx, invoker=ctx.author.id)
				if len(embedss) > 1:
					paginator.add_button('prev', emoji='<a:left:921613325920518174>', style=discord.ButtonStyle.blurple)
					#paginator.add_button('first', emoji='<:Settings:921574525815103528>', style=discord.ButtonStyle.green)
					paginator.add_button('next', emoji='<:right:921574372693651517>', style=discord.ButtonStyle.blurple)
					paginator.add_button('goto', emoji='🔢', style=discord.ButtonStyle.grey)
				return await paginator.start()





	async def on_help_command_error(self, ctx, error):
			try:
				if isinstance(error, commands.BadArgument):
					member = ctx.message.author
					em = discord.Embed(title=f" __**Help Panel**__", description=str(error), color=0xeb041c, timestamp=ctx.message.created_at)
					em.set_footer(text=f" Requested by: {ctx.message.author}")
					em.add_field(name=f"__**All Commands:**__", value='``;cmds``', inline=False)
					em.add_field(name=f"__**Command Help:**__", value="``;help [cmd]``", inline=False)
					em.add_field(name=f"__**All Categories:**__", value='``;categories``', inline=False)
					em.add_field(name=f"**links:**", value="[Support serv](https://discord.gg/EGj2GzpU9s) | [Inv blame w/o perms](https://discord.com/api/oauth2/authorize?client_id=776128410547126322&permissions=0&scope=bot) | [Inv blame with perms](https://discord.com/api/oauth2/authorize?client_id=776128410547126322&permissions=8&scope=bot)", inline=True)
					await ctx.send(embed=em)
				else:
					raise error
			except Exception as e:
				print(e)
				pass
