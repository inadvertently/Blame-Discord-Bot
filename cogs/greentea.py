import discord, asyncio, random, argparse
from discord.ext import commands
from typing import Optional, Union
from .words import random_word, WORDS

WORDS = WORDS.split("\n")
WORDS = [word.lower() for word in WORDS]

class ParserButBetter(argparse.ArgumentParser):
    def error(self, message):
        raise commands.BadArgument(message)

class games3(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.playing = {}
        self.players= {}
        self.used_words = []
        self.empty = "<:blame_empty:1017577490761396334>"
        self._sessions = {}
        self.words = WORDS #debugging
        self.count = 100

    async def greentea_embed(self):
        embed = discord.Embed(color=0x8B4513)
        embed.title = "Black Tea is about to begin!"
        embed.description = "To participate, **react** on ✅."
        embed.add_field(name="Goal:", value="You have a few seconds to write a word containing the group of **3 letters indicated**. You lose 1 HP when the time is up. You can't reuse a word already played.\n\nUse **quit** to abandon (or **exitgame** to stop the game for everyone)\n\nSettings during this cooldown:\n**--time** <number> to redefine the minimum response time, in seconds (between 3 and 50. Current: **10**)")
        return embed




    @commands.command(
        aliases = ['btea', 'greentea'],
        usages = "Send messages",
        description = "Play an imitated version of Mudaes blacktea!",
        brief = 'None',
        help = "```Example: blacktea```"
    )
    @commands.max_concurrency(1, commands.BucketType.channel)
    @commands.bot_has_permissions(add_reactions=True)
    async def blacktea(self, ctx: commands.Context, lives: Optional[int] = 3, *flags):
        """Start a game of blacktea. Specify an integer after this for lives, and use the `--timeout` flag to set the timeout"""
        if lives <= 0:
            return await ctx.send("Sorry, you need to have at least 1 life to start with")
        
        parser = ParserButBetter()
        parser.add_argument("--timeout", nargs="?", default=10, type=int)
        try:
            args = vars(parser.parse_args(flags))
        except commands.BadArgument as e:
            return await ctx.send(str(e))
        else:
            try:
                timeout = args["timeout"]
            except KeyError:
                timeout = 10

        sessions = self._sessions

        data = {}
        data["waiting"] = True 
        data["players"] = [ctx.author.id]
        sessions[ctx.channel.id] = data
        self._sessions = sessions
        message = await ctx.send(embed=await self.greentea_embed())
        react = await message.add_reaction("✅")
        new_msg1 = await ctx.send(":coffee: :coffee: :coffee: :coffee: :coffee: :coffee: :coffee: :coffee: :coffee: :coffee: :coffee: :coffee: ")
        await asyncio.sleep(2)
        new_msg2 = await new_msg1.edit(content=f":coffee: :coffee: :coffee: :coffee: :coffee: :coffee: :coffee: :coffee: :coffee: :coffee: {self.empty} {self.empty}")
        await asyncio.sleep(2)
        new_msg3 = await new_msg2.edit(content=f":coffee: :coffee: :coffee: :coffee: :coffee: :coffee: :coffee: :coffee: {self.empty} {self.empty} {self.empty} {self.empty}")
        await asyncio.sleep(2)
        new_msg4 = await new_msg3.edit(content=f":coffee: :coffee: :coffee: :coffee: :coffee: :coffee: {self.empty} {self.empty} {self.empty} {self.empty} {self.empty} {self.empty}")
        await asyncio.sleep(2)
        new_msg5 = await new_msg4.edit(content=f":coffee: :coffee: :coffee: :coffee: {self.empty} {self.empty} {self.empty} {self.empty} {self.empty} {self.empty} {self.empty} {self.empty}")
        await asyncio.sleep(2)
        new_msg6 = await new_msg5.edit(content=f":coffee: :coffee: {self.empty} {self.empty} {self.empty} {self.empty} {self.empty} {self.empty} {self.empty} {self.empty} {self.empty} {self.empty}")
        await asyncio.sleep(2)
        new_msg7 = await new_msg6.edit(content=f"{self.empty} {self.empty} {self.empty} {self.empty} {self.empty} {self.empty} {self.empty} {self.empty} {self.empty} {self.empty} {self.empty} {self.empty}")
        await asyncio.sleep(2)
        sessions = self._sessions
        sessions[ctx.channel.id]["waiting"] = False 
        self._sessions = sessions

        await self.start_blacktea(ctx, lives, timeout)
    
    async def start_blacktea(self, ctx: commands.Context, lives: int, timeout: int):
        data = self._sessions[ctx.channel.id]
        player_objects = [ctx.guild.get_member(player_id) for player_id in data["players"]]
        players = list(filter(None, player_objects))
        to_remove = []

        player_lives = {p: lives for p in data["players"]}

        if len(players) <= 1:
            del self._sessions[ctx.channel.id]
            await ctx.send("Not enough players..")

       # if not len(players):
           # del self._sessions[ctx.channel.id]
            #return await ctx.send("No participants... I would have had time to prepare a good tea.")
        
        while True:
            if not to_remove:
                pass 
            else:
                for user_id in to_remove:
                    try:
                        data["players"].remove(user_id)
                    except IndexError:
                        pass 
            player_objects = [ctx.guild.get_member(player_id) for player_id in data["players"]]
            players = list(filter(None, player_objects))
            if len(players) == 1:
                try:
                    winner = players[0]
                    return await ctx.send(f":trophy: :trophy: :trophy: {winner.mention} **won the game** :trophy: :trophy: :trophy:")
                except:
                    pass; return await ctx.send(f":trophy: :trophy: :trophy: Nobody **won the game** :trophy: :trophy: :trophy:")
            elif len(players) == 0:
                return await ctx.send("The game tied")
            to_remove = []
            for player in players:
                word = random_word()
                segment = word[:3]
                if len(segment) <= 2:
                    segment = word[:2]
                def player_check(m: discord.Message):
                    return m.author == player and m.channel == ctx.channel

                await ctx.send(f":coffee: {player.mention} Type a word containing: **{segment.upper()}**")
                try:
                    resp = await self.bot.wait_for("message", check=player_check, timeout=timeout)
                except asyncio.TimeoutError:
                    player_lives[player.id] -= 1
                    #await ctx.send(f":boom: Time's up: -1 HP (Left: **{player_lives[player.id]}** HP)")
                    if player_lives[player.id] <= 0:
                        to_remove.append(player.id)
                        await ctx.send(f":door: {player.mention} **eliminated**!")
                    await ctx.send(f":boom: Time's up: -1 HP (Left: **{player_lives[player.id]}** HP)")
                    valid_players = [user for user in players if player_lives[player.id] > 0]
                    if len(valid_players) == 1:
                        #try:
                            winner = valid_players[0]
                            return await ctx.send(f":trophy: :trophy: :trophy: {winner.mention} **won the game** :trophy: :trophy: :trophy:")
                        #except:
                           # pass; return await ctx.send(f":trophy: :trophy: :trophy: Nobody **won the game** :trophy: :trophy: :trophy:")
                    continue 
                else:
                    if segment not in resp.content.lower() or resp.content.lower() not in WORDS:
                        player_lives[player.id] -= 1
                        #await ctx.send(f":x: Wrong: -1 HP (Left: **{player_lives[player.id]}** HP)")
                        if player_lives[player.id] <= 0:
                            to_remove.append(player.id)
                            await ctx.send(f":door: {player.mention} **eliminated**!")
                        await ctx.send(f":x: Wrong: -1 HP (Left: **{player_lives[player.id]}** HP)")
                        valid_players = [user for user in players if player_lives[player.id] > 0]
                        if len(valid_players) == 1:
                            #try:
                                winner = valid_players[0]
                                return await ctx.send(f":trophy: :trophy: :trophy: {winner.mention} **won the game** :trophy: :trophy: :trophy:")
                           # except:
                               # pass; return await ctx.send(f":trophy: :trophy: :trophy: Nobody **won the game** :trophy: :trophy: :trophy:")
                        continue 
                    else:
                        await resp.add_reaction("✅")
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
        if isinstance(user, discord.User) or user.bot:
            return 
        if str(reaction.emoji) != "✅":
            return 

        sessions = self._sessions

        message: discord.Message = reaction.message 

        if message.channel.id not in sessions or sessions[message.channel.id]["waiting"] == False:
            return 
        
        if user.id in sessions[message.channel.id]["players"]:
            return
        sessions[message.channel.id]["players"].append(user.id)
        self._sessions = sessions

async def setup(bot):
    await bot.add_cog(games3(bot))