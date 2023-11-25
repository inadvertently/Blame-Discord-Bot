import discord
from discord.ext import commands
import Core.utils as util
from Core.utils import get_theme
from datetime import datetime

class taggerz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tags = self.bot.db['tags']

    @commands.hybrid_group(
        invoke_without_command=True,
        name='tag',
        aliases=['t', 'tags'],
        usage = 'manage_messages',
        description = 'Create custom tags in you server (good for support servers)',
        brief= 'None',
        help = '```Syntax: tag [subcommand] <arg>\nExample: tag create help, @support help```' 
        )
    async def tag(self, ctx, *, tag: str=None):
        try:
            check = await self.tags.find_one({ "guild_id": ctx.guild.id, "tag": tag.lower() })
            if check:
                await ctx.send(f"{check['response']}")
                uses = int(check['uses'])
                newUses = uses +1
                await self.tags.update_one({ "guild_id": ctx.guild.id, "tag": tag }, { "$set": { "uses": newUses}})
            else:
                check2 = await self.tags.find_one({ "guild_id": ctx.guild.id, "aliases": [str(tag)]})
                if check2:
                    #aliasess = check2['aliases']
                    #print(aliasess)
                    #if tag in aliasess or tag.lower() in aliasess:
                    await ctx.send(f"{check2['response']}")
                    uses = int(check2['uses'])
                    newUses = uses +1
                    return await self.tags.update_one({ "guild_id": ctx.guild.id, "aliases": tag.lower() }, { "$set": { "uses": newUses}})
                    #else:
                       # print('2222')
                       # return await util.send_error(ctx, f"The tag ``{tag}`` does not exist in this server.")
                if not check2:
                    print('1111')
                    return await util.send_error(ctx, f"The tag ``{tag}`` does not exist in this server.")
        except:
            pass
            
            embed = discord.Embed(title="Group Command: tag", description="Create custom tags within your server\n```Syntax: tag [subcommand]\nExample: tag create hi```", color = discord.Color.blurple())
            embed.set_author(name="tag help", icon_url=ctx.me.avatar.url)
            embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('tag').walk_commands()])} ・ tag backup")
            return await ctx.send(embed=embed)
        
    @tag.command(
        aliases=['new', 'add'],
        usage = 'manage_messages',
        description = 'Create custom tags in you server (good for support servers)',
        brief= 'tag, respose',
        help = '```Syntax: tag create [tag], [response]\nExample: tag create help, @support help```' 
    )
    @commands.has_permissions(manage_messages=True)
    async def create(self, ctx, *, tag):
        try:
            check = await self.tags.find_one({ "guild_id": ctx.guild.id, "tag": str(tag)})
            if check:
                return await util.send_error(ctx, f"The tag ``{tag}`` already exsists!")
            else:
                tag, resp = tag.split(",")
                time = datetime.now()
                uses = 0
                creator = ctx.author.id
                await self.tags.insert_one({
                    "guild_id": ctx.guild.id,
                    "tag": str(tag),
                    "response": str(resp),
                    "time": time,
                    "uses": uses,
                    "creator": creator,
                    "aliases": []
                })
                return await util.send_blurple(ctx, f"The tag ``{tag}`` has been successfully created")
        except:
            pass
        return await util.send_error(ctx, f"Incorrect format! Use a comma ``,`` to seperate the tag and its response")
    
    @tag.command(
        aliases=['delete', 'del'],
        usage = 'manage_messages',
        description = 'Delete an existing tag in your server',
        brief= 'tag',
        help = '```Syntax: tag remove [tag]\nExample: tag remove help```' 

    )
    @commands.has_permissions(manage_messages=True)
    async def remove(self, ctx, tag):
        check = await self.tags.find_one({ "guild_id": ctx.guild.id, "tag": str(tag)})
        if check:
            await self.tags.delete_one({ "guild_id": ctx.guild.id, "tag": str(tag)})
            return await util.send_blurple(ctx, f"Tag successfully deleted")
        else:
            return await util.send_error(ctx, f"The tag ``{tag}`` does not exist.")

    @tag.command(
        aliases=['lookup', 'details'],
        usage = 'manage_messages',
        description = 'Lookup info on a certain tag',
        brief= 'tag',
        help = '```Syntax: tag info [tag], [response]\nExample: tag info help```' 

    )
    @commands.has_permissions(manage_messages=True)
    async def info(self, ctx, *, tag):
        check = await self.tags.find_one({ "guild_id": ctx.guild.id, "tag": str(tag)})
        if check:
            time = check['time']
            uses = check['uses']
            creator = check['creator']
            creator2 = self.bot.get_user(creator)
            aliases = check['aliases']
            if aliases:
                aliases = ", ".join(aliases)
            else:
                aliases = "N/A"
            embed = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
            embed.set_author(name=creator2, icon_url=creator2.display_avatar.url)
            embed.title = tag
            embed.add_field(name='Creator', value=creator2.mention)
            embed.add_field(name='Uses', value=uses)
            embed.add_field(name='Created', value=str(discord.utils.format_dt(time, style='R')))
            embed.set_footer(text=f"aliases: {aliases}")
            await ctx.send(embed=embed)
        else:
            return await util.send_error(ctx, f"The tag ``{tag}`` does not exist.")
    
    @tag.command(
        aliases=['short'],
        usage = 'manage_messages',
        description = 'Create a custom alias for an exsisting tag',
        brief= 'tag, alias',
        help = '```Syntax: tag alias [tag], [alias]\nExample: tag alias help, help me```' 
    )
    @commands.has_permissions(manage_messages=True)
    async def alias(self, ctx, *, tag):
        try:
            tag, alias = tag.split(", ")
        except: pass; tag, alias = tag.split(",")
        check = await self.tags.find_one({ "guild_id": ctx.guild.id, "tag": str(tag)})
        if check:
            aliases = check['aliases']
            if alias in aliases:
                return await util.send_error(ctx, f"The alias ``{alias}`` already exists for the tag ``{tag}``")
            else:
                await self.tags.update_one({ "guild_id": ctx.guild.id, "tag": str(tag)}, { "$push": { "aliases": str(alias)}})
                return await util.send_blurple(ctx, f"The alias ``{alias}`` has been created for the tag ``{tag}``")
        else:
            return await util.send_error(ctx, f"The tag ``{tag}`` does not exist")




async def setup(bot):
    await bot.add_cog(taggerz(bot))