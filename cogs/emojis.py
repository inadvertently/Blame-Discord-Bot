import discord, math,re,aiohttp,json,os,sys
from discord.ext import commands
import Core.utils as utils, asyncio, functools
from Core import confirm
from Core.utils import get_theme
from io import BytesIO
try:
    import cairosvg
    svg_convert='cairo'
except:
    svg_convert="wand"
import unicodedata

class emojisS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warn=""
        self.session = bot.http_session
        
    @staticmethod
    def generate(img):
        # Designed to be run in executor to avoid blocking
        if svg_convert == "cairo":
            kwargs = {"parent_width": 1024, "parent_height": 1024}
            return BytesIO(cairosvg.svg2png(bytestring=img, **kwargs))

        else:
            return BytesIO(img)

    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def steal(self, ctx, emote=None):
            if emote == None:
                try:
                    emojis=await self.emoji_find(ctx=ctx)
                    emname=emojis.get("name")
                    emurl=emojis.get("url")
                    emid=emojis.get("id")
                except AttributeError:
                    return await ctx.reply(embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"{self.warn} {ctx.author.mention}: **no grabbable previously sent emoji detected**"))
                try:
                    message = await ctx.send(embed=discord.Embed(title=emname, color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)).add_field(name=f"Emoji ID", value=f"`{emid}`").add_field(name="Image URL", value=f"[Here]({emurl})").set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar).set_image(url=emurl).set_footer(text="react to steal"))
                except:
                    return await ctx.reply(embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f"{self.warn} {ctx.author.mention}: **no grabbable previously sent emoji detected**"))
                confirmed:bool = await confirm.confirm(self, ctx, message)
                if confirmed:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(emurl) as response:
                            img = await response.read()
                    emote=await ctx.guild.create_custom_emoji(name=emname, image=img)
                    await message.edit(view=None, embed=discord.Embed(description=f"**added emoji:** {emote}", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
                else:
                    await message.edit(view=None, embed=discord.Embed(description=f"**cancelled emoji steal**", color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)))
            else:
                name = emote.split(':')[1]
                emoji_name = emote.split(':')[2][:-1]
                anim = emote.split(':')[0]
                if anim == '<a':
                    url = f'https://cdn.discordapp.com/emojis/{emoji_name}.gif'
                else:
                    url = f'https://cdn.discordapp.com/emojis/{emoji_name}.png'
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        img = await response.read()
                emote = await ctx.guild.create_custom_emoji(name=name, image=img)
                embed = discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16)) 
                embed.set_image(url=emote.url)
                embed.description = f"<:check:921544057312915498> Stole: {emote}\nAdded as: **{name}**"
                await ctx.send(embed=embed)

    async def emoji_find(self, ctx):
        content=[]
        async for message in ctx.channel.history(limit=50):
            data = re.findall(r"<(a?):([a-zA-Z0-9\_]+):([0-9]+)>", message.content)
            for _a, emoji_name, emoji_id in data:
                animated = _a == "a"
                if animated:
                    url = "https://cdn.discordapp.com/emojis/" + emoji_id + ".gif"
                else:
                    url = "https://cdn.discordapp.com/emojis/" + emoji_id + ".png"
                name=emoji_name
                dic={}
                dic["name"]=f"{name}"
                dic['url']=f"{url}"
                dic['id']=f"{emoji_id}"
                return dic

    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def delete(self, ctx, emote : discord.Emoji = None):
        if emote == None:
            await utils.send_command_help(ctx)
            return
            
        em = discord.Embed(description=f'{emote} has been **deleted**.', color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
        await ctx.send(embed = em)
        await emote.delete()  

    @commands.command(aliases=["emotes", "emojis", "servemotes"])
    async def serveremotes(self, ctx):
        try:
            msg = ""
            for x in ctx.guild.emojis:
                if x.animated:
                    msg += "<a:{}:{}> ".format(x.name, x.id)
                else:
                    msg += "<:{}:{}> ".format(x.name, x.id)
            if msg == "":
                await ctx.send("theres no emotes bro")
                return
            else:
                i = 0 
                n = 2000
                for x in range(math.ceil(len(msg)/2000)):
                    while msg[n-1:n] != " ":
                        n -= 1
                    s=discord.Embed(description=msg[i:n], color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16))
                    i += n
                    n += n
                    if i <= 2000:
                        s.set_author(name="{} emotes".format(ctx.guild.name), icon_url=ctx.guild.icon.url)
                    await ctx.send(embed=s)
        except:
            pass


    @commands.command(name='enlarge', aliases=['e','bigemoji'],description='enlarge an emoji', brief='emoji', usage='```Swift\nSyntax: !enlarge <emoji>\nExample: !enlarge :cat:```')
    async def enlarge(self, ctx, emoji: str = None):
        """Post a large .png of an emoji"""
        if emoji is None:
            return await ctx.invoke(self.bot.get_command('eetnlarge'))
        else:
            convert = False
            if emoji[0] == "<":
                # custom Emoji
                try:
                    name = emoji.split(":")[1]
                except IndexError:
                    return await utils.send_error(ctx, f"that isn't an emoji")
                emoji_name = emoji.split(":")[2][:-1]
                if emoji.split(":")[0] == "<a":
                    # animated custom emoji
                    url = f"https://cdn.discordapp.com/emojis/{emoji_name}.gif"
                    name += ".gif"
                else:
                    url = f"https://cdn.discordapp.com/emojis/{emoji_name}.png"
                    name += ".png"
            else:
                chars = []
                name = []
                for char in emoji:
                    chars.append(hex(ord(char))[2:])
                    try:
                        name.append(unicodedata.name(char))
                    except ValueError:
                        # Sometimes occurs when the unicodedata library cannot
                        # resolve the name, however the image still exists
                        name.append("none")
                name = "_".join(name) + ".png"
                if len(chars) == 2 and "fe0f" in chars:
                    # remove variation-selector-16 so that the appropriate url can be built without it
                    chars.remove("fe0f")
                if "20e3" in chars:
                    # COMBINING ENCLOSING KEYCAP doesn't want to play nice either
                    chars.remove("fe0f")
                if svg_convert is not None:
                    url = "https://twemoji.maxcdn.com/2/svg/" + "-".join(chars) + ".svg"
                    convert = True
                else:
                    url = (
                        "https://twemoji.maxcdn.com/2/72x72/" + "-".join(chars) + ".png"
                    )
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    return await utils.send_error(ctx, f"that isn't an emoji")
                img = await resp.read()
            if convert:
                task = functools.partial(self.generate, img)
                task = self.bot.loop.run_in_executor(None, task)
                try:
                    img = await asyncio.wait_for(task, timeout=15)
                except asyncio.TimeoutError:
                    return await utils.send_error(ctx, f"Image Creation Timed Out")
            else:
                img = BytesIO(img)
            await ctx.send(file=discord.File(img, name))

async def setup(bot):
    await bot.add_cog(emojisS(bot)) 