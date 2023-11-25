from http import client
import motor.motor_asyncio, datetime, asyncio
import discord
from discord.ext import commands

list = [493545772718096386, 386192601268748289, 236522835089031170]
errorcol = 0xA90F25 # error color
urgecolor = 0xF3DD6C # exclamation color
success = discord.Colour.blurple() #theme
checkmoji = "<:blurple_check:921544108252741723>" # success emoji
xmoji = "<:yy_yno:921559254677200957>" # unsuccessful emoji
urgentmoji = "<:n_:921559211366838282>"

class LimitInput(discord.ui.Modal, title='VoiceMaster Channel Limit'):
    def __init__(self, bot):
        super().__init__()
        self.bot=bot
        self.userdb = self.bot.db['voicemasterUser']

    renamee = discord.ui.TextInput(label='rename', placeholder="what would you like the limit to be?")

    async def on_submit(self, interaction: discord.Interaction) -> None:
        find = await self.userdb.find_one({"userID": interaction.user.id})
        if find:
            data = find['channelID']
            channel = self.bot.get_channel(data)
            if int(self.renamee.value) > 99:
                embed = discord.Embed(description=f"{urgentmoji} {interaction.user.mention} please put a number below `99`", color=urgecolor)
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            await channel.edit(user_limit=int(self.renamee.value))
            embed=discord.Embed(description=f"<:check:921544057312915498> {interaction.user.mention} your **voicemaster** channel **limit** has been set to **{self.renamee.value}**", color=0x43B581)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed=discord.Embed(description=f"{urgentmoji} {interaction.user.mention} You're not connected to your **voicemaster** channel", color=errorcol)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

class RenameInput(discord.ui.Modal, title='VoiceMaster Channel Rename'):
    def __init__(self, bot):
        super().__init__()
        self.bot=bot
        self.userdb = self.bot.db['voicemasterUser']

    renamee = discord.ui.TextInput(label='rename', placeholder="what would you like to name it?")

    async def on_submit(self, interaction: discord.Interaction) -> None:
        find = await self.userdb.find_one({"userID": interaction.user.id})
        if find:
            data = find['channelID']
            channel = self.bot.get_channel(data)
            await channel.edit(name=self.renamee.value)
            embed = discord.Embed(description=f"{urgentmoji} {interaction.user.mention} your channel **name** has been set to `{self.renamee.value}`", color=urgecolor)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed=discord.Embed(description=f"{urgentmoji} {interaction.user.mention} You're not connected to your **voicemaster** channel", color=errorcol)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

async def buildEmbed(url):
    embed = discord.Embed(title="blame interface", url="https://blame.gg/discord", color=discord.Color.blurple())
    embed.add_field(name="<:lock:1005544739568885860> Lock", value="Lock's your channel so that other members cannot join it.", inline=False)
    embed.add_field(name="<:unlock:1005545076941934592> Unlock", value="Unlock's your channel so others may join it.", inline=False)
    embed.add_field(name="<a:aw_whiteuser:921807056955121714> Limit", value="Set a limit to your channel so only a certain amount may join.", inline=False)
    embed.add_field(name="<a:AN_whitecrown:1005549073870377050> Claim", value="Claim the voice channel if the creator leaves.", inline=False)
    embed.add_field(name="<:chanwhite:1005551563793772614> Name", value = "Change the name of your channel.", inline=False)
    #embed.add_field(name="<:trash:1005550877861494814> Delete", value="Delete your channel.", inline=False)
    embed.set_footer(text="The Blame Team", icon_url=str(url))
    return embed

class PersistentView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = 0
        self.bot = bot
        self.userdb = self.bot.db["voicemasterUser"]#fetching collection 1
        self.guilddb = self.bot.db["voicemasterGuild"] #fetching collection 1
        self.errorcol = 0xA90F25 # error color
        self.urgecolor = 0xF3DD6C # exclamation color
        self.success = discord.Colour.blurple() #theme
        self.checkmoji = "<:blurple_check:921544108252741723>" # success emoji
        self.xmoji = "<:yy_yno:921559254677200957>" # unsuccessful emoji
        self.urgentmoji = "<:n_:921559211366838282>" # exclamation emoji


    @discord.ui.button(emoji="<:unlock:1005545076941934592>", custom_id="Unlock_Button",label="Unlock", style=discord.ButtonStyle.blurple)
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):
        find = await self.userdb.find_one({"userID": interaction.user.id})
        if find:
            data = find['channelID']
            channel = self.bot.get_channel(data)
            await channel.set_permissions(interaction.guild.default_role, connect=True)
            embed=discord.Embed(description=f"<:check:921544057312915498> {interaction.user.mention} your **voicemaster** channel has been **unlocked**", color=0x43B581)
            
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed=discord.Embed(description=f"{self.urgentmoji} {interaction.user.mention} You're not connected to your **voicemaster** channel", color=errorcol)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(emoji="<:lock:1005544739568885860>", custom_id="Lock_Button",label="Lock", style=discord.ButtonStyle.blurple)
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        find = await self.userdb.find_one({"userID": interaction.user.id})
        if find:
            data = find['channelID']
            channel = self.bot.get_channel(data)
            await channel.set_permissions(interaction.guild.default_role, connect=False)
            embed=discord.Embed(description=f"<:check:921544057312915498> {interaction.user.mention} your **voicemaster** channel has been **locked**", color=0x43B581)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed=discord.Embed(description=f"{self.urgentmoji} {interaction.user.mention} You're not connected to your **voicemaster** channel", color=errorcol)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
   

    @discord.ui.button(emoji="<a:aw_whiteuser:921807056955121714>", custom_id="Limit_Button",label="Limit", style=discord.ButtonStyle.blurple)
    async def limit(self, interaction: discord.Interaction, button: discord.ui.Button):
        find = await self.userdb.find_one({"userID": interaction.user.id})
        if find:
            await interaction.response.send_modal(LimitInput(self.bot))
        else:
            embed=discord.Embed(description=f"{self.urgentmoji} {interaction.user.mention} You're not connected to your **voicemaster** channel", color=errorcol)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(emoji="<a:AN_whitecrown:1005549073870377050>", custom_id="Claim_Button",label="Claim", style=discord.ButtonStyle.blurple)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            find = await self.userdb.find_one({"guildID": interaction.guild.id})
            if find:
                data = find['channelID']
                ownerscrap = find['userID']
                channel = self.bot.get_channel(data)
                owner = interaction.guild.get_member(ownerscrap)
                if owner in channel.members:
                    embed=discord.Embed(description=f"{self.urgentmoji} {interaction.user.mention} You **can't** claim this channel since the **current owner** ({owner.mention}) is still here.", color=errorcol)
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    embed=discord.Embed(description=f"<:check:921544057312915498> {interaction.user.mention} you now **own** this channel", color=0x43B581)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    await channel.edit(name=f"{interaction.user}'s channel")
                    await self.userdb.update_one({ "guildID": interaction.guild.id}, { "$set": { "userID": interaction.user.id}})
            else:
                embed=discord.Embed(description=f"{self.urgentmoji} {interaction.user.mention} You're not connected to your **voicemaster** channel", color=errorcol)
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(e)


    @discord.ui.button(emoji="<:chanwhite:1005551563793772614>", custom_id="Name_Button",label="Name", style=discord.ButtonStyle.blurple)
    async def name(self, interaction: discord.Interaction, button: discord.ui.Button):
        find = await self.userdb.find_one({"userID": interaction.user.id})
        if find:
            await interaction.response.send_modal(RenameInput(self.bot))
        else:
            embed=discord.Embed(description=f"{self.urgentmoji} {interaction.user.mention} You're not connected to your **voicemaster** channel", color=errorcol)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

 
class voiceMaster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.userdb = self.bot.db["voicemasterUser"] #fetching collection 1
        self.guilddb = self.bot.db["voicemasterGuild"] #fetching collection 1
        self.errorcol = 0xA90F25 # error color
        self.urgecolor = 0xF3DD6C # exclamation color
        self.success = discord.Colour.blurple() #theme
        self.checkmoji = "<:blurple_check:921544108252741723>" # success emoji
        self.xmoji = "<:yy_yno:921559254677200957>" # unsuccessful emoji
        self.urgentmoji = "<:n_:921559211366838282>" # exclamation emoji



    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        try:
            guildID = member.guild.id
            check = await self.guilddb.find_one({"guild_id": guildID})

            if check:
                data = await self.guilddb.find_one({"guild_id": guildID})
                findit = data['voiceChannelID']
                #foundit = self.bot.get_channel(findit)
                if after.channel.id == findit:

                    categ = await self.guilddb.find_one({ "guild_id": member.guild.id })
                    category = categ['voiceCategoryID']
                    category2 = self.bot.get_channel(category)
                    name = f"{member}'s channel"
                    channel2 = await member.guild.create_voice_channel(name, category=category2)
                    channelID = channel2.id
                    await member.move_to(channel2)
                    await channel2.set_permissions(self.bot.user, connect=True,read_messages=True)
                    await self.userdb.insert_one({
                        "userID": member.id,
                        "channelName": None,
                        "channelID": None,
                        "channelLimit": None,
                        "owner": None,
                        "guildID": member.guild.id
                    })
                    await asyncio.sleep(1)
                    await self.userdb.update_one({ "userID": member.id}, { "$set": { "channelID": channel2.id}})
                    
                    #await self.userdb.update_one({ "userID": member.id}, { "$set": { "owner": member.id}})
                    #aaa = await self.userdb.find_one({ "userID": member.id})
                    #data = aaa['userID']
                    #dataget = self.bot.get_member(aaa)

                    def check(a,b,c):
                        return len(channel2.members) == 0
                    await self.bot.wait_for('voice_state_update', check=check)
                    await self.userdb.delete_many({ "userID": member.id})
                    await channel2.delete(reason="Voice channel was left empty")
                    await asyncio.sleep(3)

            else:
                return
        except Exception as e:
            return

    @commands.group(
        aliases = ['voicemaster', 'vm'],
        usage = "Send_messages",
        description = "Create your own custom/temporary voice channels through the bot",
        brief = "subcommand",
        help = "```Syntax: voicemaster [subcommand]\nExample: voicemaster setup```"
    )
    async def voice(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Group Command: voicemaster", description="Create your own custom/temporary voice channels through the bot\n```Syntax: voicemaster [subcommand]\nExample: voicemaster setup```", color = discord.Color.blurple())
                embed.set_author(name="Voicemaster help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('voice').walk_commands()])} ・ Voicemaster Settings")
                return await ctx.send(embed=embed)
        except Exception as e:
            print(e)

    @voice.command(
        usage = "Send_message",
        description = "Setup the voicemaster module ",
        brief = "None",
        help = "```Example: voicemaster setup```"
    )
    @commands.has_permissions(manage_channels=True)
    async def setup(self, ctx):
        try:
            guildID = ctx.guild.id
            check = await self.guilddb.find_one({"guild_id": guildID})
            if not check:
                guildID = ctx.guild.id
                id = ctx.author.id
                embed = discord.Embed(title=f"Setting up..", description=f"{self.urgentmoji} Please wait while I set this up!", color=self.urgecolor)
                msg = await ctx.send(embed=embed)

                await self.guilddb.insert_one({
                    "guild_id": ctx.guild.id,
                    "voiceCategoryID": None,
                    "channelLimit": None,
                    "voiceChannelID": None,
                })
                await asyncio.sleep(1)
                new_cat = await ctx.guild.create_category_channel("blame")
                interface = await ctx.guild.create_text_channel("interface", category=new_cat)
                await interface.send(embed=await buildEmbed(url=ctx.me.display_avatar.url), view=PersistentView(bot=self.bot))
                channel = await ctx.guild.create_voice_channel("Join To Create", category=new_cat)
                await self.guilddb.update_one({"guild_id": guildID}, {"$set": {"voiceCategoryID": new_cat.id}})
                await self.guilddb.update_one({"guild_id": guildID}, {"$set": {"voiceChannelID": channel.id}})
                embed2 = discord.Embed(description=f"""<:check:921544057312915498> **Blame's voicemaster has now been setup!** You can use the commands to control it!""", color=0x43B581) 
                await msg.edit(embed=embed2)
            else:
                failembed = discord.Embed(description=f"{self.urgentmoji} **The voicemaster module is already enabled therefore, there is nothing to setup**", color=self.urgecolor)
                return await ctx.send(embed=failembed)
        except Exception as e:
            fail = discord.Embed(description=f"```{e}```", color=self.urgecolor)
            return await ctx.send(embed=fail)

    @voice.command(
        usage = "Send_messages",
        description = "Lock's your channel so that other members cannot join it.",
        brief = "None",
        help = "```Example: voicemaster lock```"
    )
    async def lock(self, ctx):
            check2 = await self.guilddb.find_one({"guild_id": ctx.guild.id})
            if check2:
                find = await self.userdb.find_one({"userID": ctx.author.id})
                if find:
                    channel = self.bot.get_channel(find['channelID'])
                    await channel.set_permissions(ctx.guild.default_role, connect=False)
                    return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} your **voicemaster** channel has been **locked**", color=0x43B581))
                else:
                    return await ctx.send(embed=discord.Embed(description=f"{self.urgentmoji} {ctx.author.mention} You're not connected to your **voicemaster** channel", color=errorcol))
                #await ctx.send(embed=await buildEmbed(url=ctx.me.display_avatar.url), view=test(ctx, bot=self.bot))
            else:
                return await ctx.send(embed=discord.Embed(description=f"{xmoji} The voicemaster module has not been setup properly in this server. Please ask an admin to set it up", color=errorcol))


    @voice.command(
        usage = "Send_messages",
        description = "Unlock's your channel so others may join it.",
        brief = "None",
        help = "```Example: voicemaster unlock```"
    )
    async def unlock(self, ctx):
            check2 = await self.guilddb.find_one({"guild_id": ctx.guild.id})
            if check2:
                find = await self.userdb.find_one({"userID": ctx.author.id})
                if find:
                    channel = self.bot.get_channel(find['channelID'])
                    await channel.set_permissions(ctx.guild.default_role, connect=True)
                    return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} your **voicemaster** channel has been **unlocked**", color=0x43B581))
                else:
                    return await ctx.send(embed=discord.Embed(description=f"{self.urgentmoji} {ctx.author.mention} You're not connected to your **voicemaster** channel", color=errorcol))

                #await ctx.send(embed=await buildEmbed(url=ctx.me.display_avatar.url), view=test(ctx, bot=self.bot))
            else:
                return await ctx.send(embed=discord.Embed(description=f"{xmoji} The voicemaster module has not been setup properly in this server. Please ask an admin to set it up", color=errorcol))

    @voice.command(
        usage = "Send_messages",
        description = "Set a limit to your channel so only a certain amount may join.",
        brief = "limit",
        help = "```Syntax: voicemaster limit [limit]\nExample: voicemaster limit```"
    )
    async def limit(self, ctx, limit: int):
            check2 = await self.guilddb.find_one({"guild_id": ctx.guild.id})
            if check2:

                find = await self.userdb.find_one({"userID": ctx.author.id})
                if find:
                    channel = self.bot.get_channel(find['channelID'])
                    if limit <99:
                        await channel.edit(user_limit=limit)
                        return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} your **voicemaster** channel **limit** has been set to **{limit}**", color=0x43B581))
                

                    else:
                        return await ctx.send(embed=discord.Embed(description=f"{self.urgentmoji} {ctx.author.mention} **Limit** must be **smaller** than 99.", color=errorcol))
                            #cc= f":x: Limit must be a number smaller than 99."
                else:            #return await ctx.send(content=cc)
                    return await ctx.send(embed=discord.Embed(description=f"{self.urgentmoji} {ctx.author.mention} You're not connected to your **voicemaster** channel", color=errorcol))
            else:
                return await ctx.send(embed=discord.Embed(description=f"{xmoji} The voicemaster module has not been setup properly in this server. Please ask an admin to set it up", color=errorcol))

    @voice.command(
        usage = "Send_messages",
        description = "Claim the voice channel if the creator leaves.",
        brief = "None",
        help = "```Example: voicemaster claim```"
    )
    async def claim(self, ctx):
            check2 = await self.guilddb.find_one({"guild_id": ctx.guild.id})
            if check2:
                find = await self.userdb.find_one({"guildID": ctx.guild.id})
                if find:
                    ownerscrap = find['userID']
                    channel = self.bot.get_channel(find['channelID'])
                    owner = ctx.guild.get_member(ownerscrap)
                    if owner == ctx.author:
                        return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} **you already own this channel**", color=0x43B581))
                    if owner == channel.members[0]:
                        return await ctx.send(embed=discord.Embed(description=f"{self.urgentmoji} {ctx.author.mention} You **can't** claim this channel since the **current owner** ({owner.mention}) is still here.", color=errorcol))
                        #return await ctx.send(f"{ctx.author.mention}, You can't claim this channel since the current owner ({owner.mention}) is still here.", ephemeral=True)
                    if not owner == channel.members[0]:
                        await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} you now **own** this channel", color=0x43B581))
                        await channel.edit(name=f"{ctx.author}'s channel")
                        await self.userdb.update_one({ "guildID": ctx.guild.id}, { "$set": { "userID": ctx.author.id}})
                else:            #return await ctx.send(content=cc)
                    return await ctx.send(embed=discord.Embed(description=f"{self.urgentmoji} {ctx.author.mention} You're not connected to your **voicemaster** channel", color=errorcol))
                #await ctx.send(embed=await buildEmbed(url=ctx.me.display_avatar.url), view=test(ctx, bot=self.bot))
            else:
                return await ctx.send(embed=discord.Embed(description=f"{xmoji} The voicemaster module has not been setup properly in this server. Please ask an admin to set it u", color=errorcol))
    
    
    
    
    @voice.command(
        usage = "Send_messages",
        description = "Change the name of your channel.",
        brief = "name",
        help = "```Syntax: voicemaster name [name]\nExample: voicemaster name```"
    )
    async def name(self, ctx, name: str):
            check2 = await self.guilddb.find_one({"guild_id": ctx.guild.id})
            if check2:
                find = await self.userdb.find_one({"userID": ctx.author.id})
                if find:
                    channel = self.bot.get_channel(find['channelID'])
                    if len(name) < 30:
                        await channel.edit(name=name)
                        return await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} your **voicemaster** channel **name** has been set to **{name}**", color=0x43B581))
                    #cc= f"Your channel name has been changed to **{msgz.content.lower()}**"
                    #return await interaction.edit_original_message(content=cc)
                    else:
                        return await ctx.send(embed=discord.Embed(description=f"{self.urgentmoji} {ctx.author.mention} The channel **name** cannot be **longer** than **30 characters**", color=errorcol))
                        #await msgz.add_reaction('❌')
                        #return await interaction.edit_original_message(content=dd)
                else:            #return await ctx.send(content=cc)
                    return await ctx.send(embed=discord.Embed(description=f"{self.urgentmoji} {ctx.author.mention} You're not connected to your **voicemaster** channel", color=errorcol))
            else:
                return await ctx.send(embed=discord.Embed(description=f"{xmoji} The voicemaster module has not been setup properly in this server. Please ask an admin to set it u", color=errorcol))

    @voice.command(
        usage = 'administrator',
        description = 'Force reset voicemaster',
        brief = 'None',
        help = "```Example: voicemaster forcereset```"
    )
    @commands.has_permissions(administrator=True)
    async def forcereset(self, ctx):
        check = await self.guilddb.find_one({"guild_id": ctx.guild.id})
        if check:
            await self.guilddb.delete_many({"guild_id": ctx.guild.id})
            try:
                await self.userdb.delete_many({"guild_id": ctx.guild.id})
            except:
                pass
            await ctx.send(embed=discord.Embed(description=f"<:check:921544057312915498> {ctx.author.mention} Voicemaster has been **reset** in this guild. Use ``vm setup`` to redo it", color=0x43B581))
            
        else:
            return await ctx.send(embed=discord.Embed(description=f"{self.urgentmoji} {ctx.author.mention} There is no existing voicemaster setup in this guild", color=errorcol))

    @voice.command(
        usage = 'administrator',
        description = "Send the voicemaster interface you deleted it",
        brief = "None",
        help = "```Example: vm interface```"
    )
    async def interface(self,ctx):
        check = await self.guilddb.find_one({"guild_id": ctx.guild.id})
        if check:
            await ctx.channel.send(embed=await buildEmbed(url=ctx.me.display_avatar.url), view=PersistentView(bot=self.bot))
        else:
            return await ctx.send(embed=discord.Embed(description=f"{self.urgentmoji} {ctx.author.mention} There is no existing voicemaster setup in this guild. Use ``vm setup`` to create it.", color=errorcol))





async def setup(bot):
    await bot.add_cog(voiceMaster(bot))