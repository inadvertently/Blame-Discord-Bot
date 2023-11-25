import discord, textwrap, motor.motor_asyncio, asyncio
from discord.ext import commands, tasks
from colorama import Fore as f
from discord.ext.commands.cooldowns import BucketType


errorcol = 0xA90F25
urgecolor = 0xF3DD6C
success = discord.Colour.blurple()
checkmoji = "<:blurple_check:921544108252741723>"
xmoji = "<:yy_yno:921559254677200957>"
urgentmoji = "<:n_:921559211366838282>"
errmsg = "<:yy_yno:921559254677200957> Internal server error occured. Report this [here](https://discord.gg/k9q6JUBHwP)"

class join_dm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db['joindm']
        self.dms = {}
        self.clearJoindm.start()

    @tasks.loop(seconds=60)
    async def clearJoindm(self):
        try:
            self.dms.clear()
            print(f"{f.LIGHTRED_EX}[{f.RESET}{f.BLUE}(JOINDM SESSION CLEARED){f.RESET}{f.LIGHTRED_EX}]{f.RESET} {f.GREEN}->{f.RESET} {f.LIGHTGREEN_EX}JOINDM UNPAUSED{f.RESET}")
        except: pass; return

    @clearJoindm.before_loop
    async def before_clearJoindm(self):
        await self.bot.wait_until_ready()
        print(f"{f.LIGHTRED_EX}[{f.RESET}{f.BLUE}(Loop Created){f.RESET}{f.LIGHTRED_EX}]{f.RESET} {f.GREEN}->{f.RESET} {f.LIGHTGREEN_EX}JOINDM SESSION -> LISTENING...{f.RESET}")
   
    @commands.group()
    async def joindm(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Group Command: joindm", description="Greet members who join your server with a welcome DM's\n```Syntax: joindm [subcommand] <arg>\nExample: joindm message hi new members```", color = discord.Color.blurple())
                embed.set_author(name="joindm help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('joindm').walk_commands()])} ・ Joindm Settings")
                return await ctx.send(embed=embed)
        except Exception as e:
            print(e)

    @joindm.command(
        aliases = ['setup', 'on'],
        usage = "Manage_guild",
        description = "Enable the joindm to start sending members who join your server, a custom dm.",
        brief = 'None',
        help="```Example: joindm enable```"
    )
    @commands.has_permissions(administrator=True)
    async def enable(self, ctx):
        try:
            async with ctx.typing():
                check = await self.db.find_one({ "guild_id": ctx.guild.id})
                if not check:
                    await self.db.insert_one({
                        "guild_id": ctx.guild.id,
                        "message": None,
                        "joindm": None,
                    })
                    await asyncio.sleep(1)
                    await self.db.update_one({"guild_id": ctx.guild.id}, {"$set": {"joindm": "Enabled"}})
                    await ctx.send(embed=discord.Embed(description="<:check:921544057312915498> The **joindm module** has been enabled.", color=0x43B581))
                else:
                    return await ctx.send(embed=discord.Embed(description=f"{xmoji} The **joindm module** has already been **enabled** in this guild", color=errorcol))
        except:
            pass

    @joindm.command(
        aliases = ['off'],
        usage = "Manage_guild",
        description = "Disable the join dm module",
        brief = "None",
        help = "```Example: joindm disable```"
    )
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx):
        try:
            check = await self.db.find_one({ "guild_id": ctx.guild.id})
            if check:
                await self.db.delete_one({ "guild_id": ctx.guild.id })
                return await ctx.send(embed=discord.Embed(description="<:check:921544057312915498> The **joindm module** has been **disabled**.", color=0x43B581))
            else:
                return await ctx.send(embed=discord.Embed(description=f"{xmoji} The **joindm module** is not **enabled**", color=errorcol))
           # return await ctx.send(embed=discord.Embed(description="I disabled the joindm module :thumbsup:", color=0xF2A0FD))
        except:
            pass

    @joindm.command(
        aliases = ['msg'],
        usage = "Manage_guild",
        description = "Set the custom welcome message that the joindm will send",
        brief = "message",
        help = """```Syntax: joindm message [message]\nExample: joindm message hiiii```"""
    )
    @commands.has_permissions(administrator=True)
    @commands.cooldown(3, 14, BucketType.user)
    async def message(self, ctx, *, message):
        try:
            check = await self.db.find_one({ "guild_id": ctx.guild.id})
            if check:
                embed=discord.Embed(description=f"<:check:921544057312915498> **The current joindm message is set to**\n```{message}```", color=0x43B581)
                embed.set_footer(text="joindm message [message] to update it", icon_url=ctx.author.display_avatar.url)
                await self.db.update_one({"guild_id": ctx.guild.id}, {"$set": {"message": message}})
                return await ctx.send(embed=embed)
            else: 
                await self.db.insert_one({
                    "guild_id": ctx.guild.id,
                    "message": message,
                    "joindm": "Enabled"
                })
                return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> The **joindm message** has now been set to:\n```{message}```", color=0x43B581))
        except Exception as e:
            print(e)
            return await ctx.send(embed=discord.Embed(description=f"{xmoji} The **joindm module** is not **enabled**", color=errorcol))


    @joindm.command(
        aliases = ['view'],
        usage = "Manage_guild",
        description = "View the current joindm message",
        brief = "None",
        help = "```Example: joindm test```"
    )
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(3, 14, BucketType.user)
    async def test(self, ctx):
        try:
            check = await self.db.find_one({ "guild_id": ctx.guild.id})
            if check:
                message = check['message']
                member = ctx.message.author
                view = discord.ui.View()
                name = textwrap.shorten(f'{ctx.guild.name}', width=55, placeholder='...')
                view.add_item(discord.ui.Button(label=f"Sent from: {name}", disabled=True))
                if "$(user)" in message:
                    message = message.replace("$(user)", str(member))
                if "$(user.mention)" in message:
                    message = message.replace("$(user.mention)", str(member.mention))
                if "$(user.name)" in message:
                    message = message.replace("$(user.name)", str(member.name))
                if "$(user.avatar)" in message:
                    message = message.replace("$(user.avatar)", str(member.avatar.url))
                if "$(user.joined_at)" in message:
                    message = message.replace("$(user.joined_at)", discord.utils.format_dt(member.joined_at, style="R"))
                if "$(user.discriminator)" in message:
                    message = message.replace("$(user.discriminator)", str(member.discriminator))

                if "$(guild.name)" in message:
                    message = message.replace("$(guild.name)", str(member.guild.name))
                if "$(guild.count)" in message:
                    message = message.replace("$(guild.count)", str(member.guild.member_count))
                if "$(guild.id)" in message:
                    message = message.replace("$(guild.id)", str(member.guild.id))
                if "$(guild.created_at)" in message:
                    message = message.replace("$(guild.created_at)", discord.utils.format_dt(member.guild.created_at, style="R"))
                if "$(guild.boost_count)" in message:
                    message = message.replace("$(guild.boost_count)", str(member.guild.premium_subscription_count))
                if "$(guild.boost_tier)" in message:
                    message = message.replace("$(guild.boost_tier)", str(member.guild.premium_tier))
                if "$(guild.icon)" in message:
                    message = message.replace("$(guild.icon)", str(member.guild.icon.url))
                await member.send(message, view=view)
                await ctx.send(":thumbsup:")
            else:
                return await ctx.send(embed=discord.Embed(description=f"{xmoji} The **joindm module** is not **enabled**", color=errorcol))
        except Exception as e:
            print(e);pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            guild =  member.guild
            try:
                self.dms[guild.id]
            except KeyError:
                self.dms[guild.id] = 1
            self.dms[guild.id] = self.dms[guild.id]+1
            message1 = await self.db.find_one({"guild_id": guild.id})
            if message1 and not self.dms[guild.id] >= 20:
                message = message1['message']
                chec = await self.db.find_one({"guild_id": guild.id})
                check = chec['joindm']
                view = discord.ui.View()
                name = textwrap.shorten(f'{member.guild.name}', width=55, placeholder='...')
                view.add_item(discord.ui.Button(label=f"Sent from: {name}", disabled=True))
                view.disabled = True
                if "$(user)" in message:
                    message = message.replace("$(user)", str(member))
                if "$(user.mention)" in message:
                    message = message.replace("$(user.mention)", str(member.mention))
                if "$(user.name)" in message:
                    message = message.replace("$(user.name)", str(member.name))
                if "$(user.avatar)" in message:
                    message = message.replace("$(user.avatar)", str(member.avatar.url))
                if "$(user.joined_at)" in message:
                    message = message.replace("$(user.joined_at)", discord.utils.format_dt(member.joined_at, style="R"))
                if "$(user.discriminator)" in message:
                    message = message.replace("$(user.discriminator)", str(member.discriminator))

                if "$(guild.name)" in message:
                    message = message.replace("$(guild.name)", str(member.guild.name))
                if "$(guild.count)" in message:
                    message = message.replace("$(guild.count)", str(member.guild.member_count))
                if "$(guild.id)" in message:
                    message = message.replace("$(guild.id)", str(member.guild.id))
                if "$(guild.created_at)" in message:
                    message = message.replace("$(guild.created_at)", discord.utils.format_dt(member.guild.created_at, style="R"))
                if "$(guild.boost_count)" in message:
                    message = message.replace("$(guild.boost_count)", str(member.guild.premium_subscription_count))
                if "$(guild.boost_tier)" in message:
                    message = message.replace("$(guild.boost_tier)", str(member.guild.premium_tier))
                if "$(guild.icon)" in message:
                    message = message.replace("$(guild.icon)", str(member.guild.icon.url))

                if "Enabled" in check:
                    await member.send(f"{message}", view=view)

                if message1 == None:
                    return
            else:
                return
        except:
            return

async def setup(client): 
    await client.add_cog(join_dm(client))