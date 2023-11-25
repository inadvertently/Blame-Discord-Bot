import discord, motor, asyncio, typing, Core.confirm as cop_is_gae
from discord.ext import commands
from random import *
from PIL import Image
from io import BytesIO


class juulS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db['juuls']


    @commands.group()
    async def juul(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Command: juul", description="Start smoking eachothers pack by passing a juul around your server\n```Syntax: antinuke [subcommand] <arg>\nExample: juul pass @obsidian``` ", color = discord.Color.blurple())
                embed.set_author(name="Juul help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('juul').walk_commands()])} ・ Juul")
                return await ctx.send(embed=embed)
        except Exception as e:
            print(e)
    
    @juul.command(
        name = "pass",
        aliases = ['give', 'slide'],
        usage = "Send_messages",
        description = "Pass a friend the juul and let em smoke a pack",
        brief = "member",
        help = "```Syntax: juul pass [member]\nExample: juul pass @obsidian```"
    )
    async def pas(self, ctx, member: discord.Member):
        findjuul = await self.db.find_one({ "guild_id": ctx.guild.id })
        if findjuul:
            data = findjuul['currentUser']
            if ctx.author.id == data:
                await ctx.send(f"You **passed** the juul to {member.mention} <:2joesmoke:1005669384313913397>")
                await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "currentUser": member.id}})
            else:
                return await ctx.send("<:pe_clown:1005671310808055969> you <:pe_clown:1005671310808055969> don't <:pe_clown:1005671310808055969> even <:pe_clown:1005671310808055969> have <:pe_clown:1005671310808055969> the <:pe_clown:1005671310808055969> juul <:pe_clown:1005671310808055969>right <:pe_clown:1005671310808055969> now <:pe_clown:1005671310808055969> buddy.. <:pe_clown:1005671310808055969> don't <:pe_clown:1005671310808055969> get <:pe_clown:1005671310808055969> caught <:pe_clown:1005671310808055969> lacking <:pe_clown:1005671310808055969> again <:pe_smoke:1005671836459225159>")
        else:
            return await ctx.send(f"There is no juul in **{ctx.guild.name}** To create one use ``juul create`` <a:pepesmoke:1005670761542975508>")
    
    @juul.command(
        aliases = ['del', 'delete'],
        usage = "manage_messages",
        decription = "Burn out the juul so no one gets it back (including you)",
        brief = "None",
        help = "```Example: juul burnout```"
    )
    @commands.has_permissions(manage_messages=True)
    async def burnout(self, ctx):
        findjuul = await self.db.find_one({ "guild_id": ctx.guild.id })
        if findjuul:
            data = findjuul['currentUser']
            await ctx.send(f"ight.. <@{data}> yo, {ctx.author.mention} couldn't handle getting his pack smoked so he burned out the juul <:TNT_0sad:1005674254370611231> ")
            await self.db.delete_one({ "guild_id": ctx.guild.id })
        else:
            return await ctx.send(f"where do you see a juul bro? use ``juul create``")
    
    @juul.command(
        aliases = ['buy', 'start'],
        usage = "manage_messages",
        description = "Create a juul in your server so members can smoke eachothers pack and develop cancer for smoking <:idksmoke:1005669492396916769>",
        brief = "None",
        help = "```Example: juul create```"
    )
    @commands.has_permissions(manage_messages=True)
    async def create(self, ctx):
        async with ctx.typing():
            findjuul = await self.db.find_one({ "guild_id": ctx.guild.id })
            if not findjuul:
                await self.db.insert_one({
                "guild_id": ctx.guild.id,
                "currentUser": ctx.author.id,
                "smokes": randint(1,100)})
                await asyncio.sleep(1)
                find = await self.db.find_one({ "guild_id": ctx.guild.id })
                dat = find['smokes']
                return await ctx.send(f"you just got your hands on a juul and it has **{dat}%** battery left.. :battery:")
            else:
                finder = findjuul['currentUser']
                return await ctx.send(f"stop smoking pal, you're losing too many braincells.. a juul **already exists** and is in <@{finder}>'s posession ")

    @juul.command(
        aliases = ['rob', 'take', 'finesse'],
        usage = 'None',
        description = "Steal the juul from the current holder",
        brief = "None",
        help = "```Example: juul finesse``"
    )
    async def steal(self, ctx):
        findjuul = await self.db.find_one({ "guild_id": ctx.guild.id })
        if findjuul:
            if ctx.author.guild_permissions.manage_messages:
                person = findjuul['currentUser']
                g = f"are you sure you want to **finesse the juul** from <@{person}>? This is a criminal offense btw so take this, https://www.criminaldefenselawyer.com/topics/crimes-against-property-taking-what-isnt-yours"
                msg = await ctx.send(g)
                async def confirm():
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "currentUser ": ctx.author.id}})
                    cnt = f"{ctx.author.mention}, nice job, you just comiited a **criminal offense**.. lets get to smoking more packs <:2joesmoke:961829211969048646>  "
                    await msg.edit(content=cnt)

                async def cancel():
                    nt = f" damn, you should've stole it <:RE_pepefacepalm:1005683933234606080> "
                    await msg.edit(content=nt)
                    pass

                confirmed:bool = await cop_is_gae.confirm(self, ctx, msg)
                if confirmed:
                    await confirm()
                else:
                    await cancel()
            else:
                return await ctx.send("Only staff can use this command buddy <a:pepesmoke:1005670761542975508> ")
        else:
            return await ctx.send("no juul has even been created bro. Use ``juul create``")

    @juul.command(
        aliases = ["puff", 'hit', 'wiff'],
        usage = "Send_messages",
        description = "Smoke someones pack real quick if you have the juul in posession",
        brief = "member",
        help = "```Syntax: juul smoke [member]\nExample juul smoke @obsidian```"
    )
    async def smoke(self, ctx, member: discord.Member):
        findjuul = await self.db.find_one({ "guild_id": ctx.guild.id })
        if findjuul:
            data = findjuul['currentUser']
            if ctx.author.id == data:
                battery = findjuul['smokes']
                bat = int(battery)
                if bat == 0 or bat == 1:
                    await ctx.send("**THE JUUL JUST RAN OUT OF BATTERY** GET A NEW ONE USING ``juul create``")
                    return await self.db.delete_one({ "guild_id": ctx.guild.id })
                else:
                    total = bat - 1
                    await self.db.update_one({ "guild_id": ctx.guild.id }, { "$set": { "smokes": total}})
                    #getsmoked = Image.open("GETSMOKED.png")
                # asset = member.display_avatar.with_size(128)
                # data = BytesIO(await asset.read())
                # pfp = Image.open(data)
                    #pfp = pfp.resize((256,256))
                    #getsmoked.paste(pfp)
                    #g#etsmoked.save("getsmoked2.png")
                    return await ctx.send(f"{member.mention} BRO JUST GOT SMOKED :wheelchair: :airplane: :dash: :fire_engine: :fire_extinguisher:\nthe juul now has **{total}%** battery :battery:")
            else:
                return await ctx.send("The juul is not in your posession bozo")
        else:
            return await ctx.send("No juul has been created in this server yet. Use ``juul create``")
                
async def setup(bot):
	await bot.add_cog(juulS(bot))

    


