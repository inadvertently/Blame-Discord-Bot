import motor.motor_asyncio, datetime, asyncio
import discord
from discord.ext import commands
from pyparsing import col

list = [493545772718096386, 386192601268748289, 236522835089031170]

class guildPercS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.errorcol = 0xA90F25 # error color
        self.urgecolor = 0xF3DD6C # exclamation color
        self.success = discord.Colour.blurple() #theme
        self.checkmoji = "<:blurple_check:921544108252741723>" # success emoji
        self.xmoji = "<:yy_yno:921559254677200957>" # unsuccessful emoji
        self.urgentmoji = "<:n_:921559211366838282>" # exclamation emoji
        self.db = self.bot.db["userCommands"]

    @commands.command(
        usage = "Must be in support server",
        description = "Claim perks based on the size of servers you own in which blame is used in! \n**In easier terms:** if you own a server with a **membercount of 1K** in which blame is used in, you will get roles/perks in the support server for it!",
        brief = "None",
        help = "```Example: claim```"
    )
    async def claim2 (self, ctx):
        guild = self.bot.get_guild(818179462918176769)
        try:
            if not ctx.guild.id == 818179462918176769:
                return await ctx.message.add_reaction("❌")
            if ctx.guild.id == 818179462918176769:
                collection = []
                for s in self.bot.guilds:
                    if str(ctx.message.author) == str(s.owner):
                        collection.append(s.member_count)
                print(collection)
                if len(collection) <= 0:
                    return await ctx.send(":cry: You do not own any of the guilds I am in ")
                else:
                    get = max(collection)
                    if get > 1000: 
                        role = guild.get_role(1003846548385435711)
                        if role in ctx.author.roles:
                            return await ctx.send("You've already claimed your perks!")
                        await ctx.author.add_roles(role)
                        embed = discord.Embed(color=0x43B581)
                        embed.description = f"<:check:921544057312915498> **You've been given the role:** {role.mention}. Thanks for using me in your servers :D"
                        return await ctx.send(f"Perks claimed by {ctx.author.mention}", embed=embed)

                    if get > 5000: 
                        role = guild.get_role(1003843257744240762)
                        if role in ctx.author.roles:
                            return await ctx.send("You've already claimed your perks!")
                        await ctx.author.add_roles(role)
                        embed = discord.Embed(color=discord.Color.blurple())
                        embed.description = f"<:check:921544057312915498> **You've been given the role:** {role.mention}. dawg, thanks for using me in your servers!"
                        return await ctx.send(f"Perks claimed by {ctx.author.mention}", embed=embed)

                    if get > 10000: 
                        role = guild.get_role(907786882665041970)
                        if role in ctx.author.roles:
                            return await ctx.send("You've already claimed your perks!")
                        await ctx.author.add_roles(role)
                        embed = discord.Embed(color=0x8c1afa)
                        embed.description = f"<:check:921544057312915498> **You've been given the role:** {role.mention}. what a legend.. thanks for using me in your servers breh a:spy:921753830859870229>"
                        return await ctx.send(f"Perks claimed by {ctx.author.mention}", embed=embed)
        
                    if get > 25000: 
                        role = guild.get_role(1003844326918471754)
                        if role in ctx.author.roles:
                            return await ctx.send("You've already claimed your perks!")
                        await ctx.author.add_roles(role)
                        embed = discord.Embed(color=0xf10745)
                        embed.description = f"<:check:921544057312915498> **You've been given the role:** {role.mention}. okay mr. famous, thanks for using me in your servers like a Top G"
                        return await ctx.send(f"Perks claimed by {ctx.author.mention}", embed=embed)

                    if get > 50000: 
                        role = guild.get_role(1003845669183828020)
                        if role in ctx.author.roles:
                            return await ctx.send("You've already claimed your perks!")
                        await ctx.author.add_roles(role)
                        embed = discord.Embed()
                        embed.description = f"<:CB_poop:921544088019406968> **you're insane bro.. u partially broke me but I gave you the role** {role.mention}. Thanks for using me in your servers and feel free to message the devs for suggestions/additions :D"
                        return await ctx.send(f"Perks claimed by {ctx.author.mention}", embed=embed)
                    else:
                        return await ctx.send(":frowning: None of your servers are large enough to claim perks for")
        except Exception as e:
            print(e)

    @commands.command(
        usage = "Must be in support server",
        description = "Claim perks based on the amount of interaction you have with the bot!",
        brief = "None",
        help = "```Example: claim```"
    )
    async def claim (self, ctx):
        if ctx.guild.id == 818179462918176769:
            findauthor = await self.db.find_one({"author": ctx.author.id})
            if findauthor:
                addcount = findauthor['count']
                roles = {50: 1040982042638299146, 100: 1040982123659669596, 250: 1040982158237520033, 500: 1040982148963897346, 850: 1040982273731858462, 1000: 1040982276403630100, 1500: 1040982354329604177, 2000: 1040982351896916008, 2500: 1040995789234786364, 2700: 1040995789234786364, 3000: 1040995678656143421, 3100: 1040995678656143421, 3500: 1040982399225430077, 5000: 1040982452312735794}
                guild =self.bot.get_guild(818179462918176769)
                reg = [i.id for i in ctx.author.roles]
                newroles = [guild.get_role(roles[i]) for i in roles if addcount >= i and not roles[i] in reg]
                names = [guild.get_role(roles[i]).name for i in roles if addcount >= i and not roles[i] in reg]
                if len(names):
                    await ctx.reply(embed=discord.Embed(title="Claimed Commands 🎁", description = f"Congrats, **you claimed the roles: {', '.join(names)}**. Thanks for continously using blame!", color=discord.Color.blurple()).set_thumbnail(url="https://cdn.discordapp.com/attachments/851633587915587615/1041002010436186133/1f381.png"))   
                    return await ctx.author.add_roles(*newroles)
                else:
                    return await ctx.send("You don't qualify for any perks :/") 
            else:
                return await ctx.send("You don't qualify for any perks :/") 
        else:
            return await ctx.send("This command can only be used in the support server!")

async def setup(bot):
    await bot.add_cog(guildPercS(bot))