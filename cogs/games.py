import discord_games as games
import discord

# import base module
from discord_games import button_games
from discord.ext import commands




class games2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="hangman",
        aliases = ['hang'],
        usage = "send_messages",
        description = "Play a game of hangman",
        help = "```Example: hangman```")
    async def hangman(self, ctx: commands.Context[commands.Bot]):
        game = games.Hangman()
        await game.start(ctx, delete_after_guess=True)

    @commands.command(
        name="tictactoe",
        aliases = ['ttt'],
        usage = "send_messages",
        brief = 'user',
        description = "Play a game of tictactoe with someone",
        help = "```Syntax: ttt [user]\nExample: ttt @jacob```")
    async def tictactoe(
        self, ctx: commands.Context[commands.Bot], member: discord.User
    ):
        game = button_games.BetaTictactoe(cross=ctx.author, circle=member)
        await game.start(ctx)

    @commands.command(
        aliases = ['word', 'wordle'],
        usage = "send_messages",
        description = "Play a game of wordle",
        help = "```Example: wordle```")
    async def worldles(self, ctx: commands.Context[commands.Bot]):
        game = button_games.BetaWordle()
        await game.start(ctx)




    @commands.command(
        aliases = ['memory', 'memorygame'],
        usage = "send_messages",
        description = "Test your memory",
        help = "```Example: memorygame```")
    async def memory_games(self, ctx: commands.Context[commands.Bot]):

        game = button_games.MemoryGame()
        await game.start(ctx)

    @commands.command(
        aliases = ['rock', 'paper', 'scissors', 'rps'],
        usage = "send_messages",
        description = "Play a game of rps",
        help = "```Example: rps```")
    async def rpss(
        self, ctx: commands.Context[commands.Bot], player: discord.User = None
    ):

        game = button_games.BetaRockPaperScissors(
            player
        )  # defaults to playing with bot if player = None
        await game.start(ctx)


    @commands.command(
        aliases = ['c4', 'connect4'],
        usage = "send_messages",
        description = "Play a game of connect four with someone",
        brief = 'user',
        help = "```Syntax: c4 [user]\nExample: c4 @jacob```")
    async def connect44(self, ctx: commands.Context[commands.Bot], member: discord.User):
        game = games.ConnectFour(
            red=ctx.author,
            blue=member,
        )
        await game.start(ctx)

    @commands.command(
        aliases = ['typeracer', 'tr', 'type', 'typerace'],
        usage = "send_messages",
        description = "Test your typing speed",
        help = "```Example: tr```")
    async def typeraces(self, ctx: commands.Context[commands.Bot]):
        game = games.TypeRacer()
        await game.start(ctx, timeout=30)

    @commands.group(aliases=['games'])
    async def game(self, ctx):
        try:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(title="Command: game", description="Games to play with your server members or friends\n```Syntax: game [subcommand] <argument>\nExample: game tictactoe @jacob```", color = discord.Color.blurple())
                embed.set_author(name="game help", icon_url=ctx.me.avatar.url)
                embed.set_footer(text=f"Page 1/{len([sc for sc in self.bot.get_command('game').walk_commands()])} ・ game")
                return await ctx.send(embed=embed)
        except Exception as e:
            print(e) 

    @game.command(
        name="hangman",
        aliases = ['hang'],
        brief = 'None',
        usage = "send_messages",
        description = "Play a game of hangman",
        help = "```Example: hangman```")
    async def hangman(self, ctx: commands.Context[commands.Bot]):
        game = games.Hangman()
        await game.start(ctx, delete_after_guess=True)

    @game.command(
        name="tictactoe",
        aliases = ['ttt'],
        usage = "send_messages",
        brief = 'user',
        description = "Play a game of tictactoe with someone",
        help = "```Syntax: ttt [user]\nExample: ttt @jacob```")
    async def tictactoe(
        self, ctx: commands.Context[commands.Bot], member: discord.User
    ):
        game = button_games.BetaTictactoe(cross=ctx.author, circle=member)
        await game.start(ctx)

    @game.command(
        aliases = ['word', 'wordle'],
        usage = "send_messages",
        brief = 'None',
        description = "Play a game of wordle",
        help = "```Example: wordle```")
    async def worldle(self, ctx: commands.Context[commands.Bot]):
        game = button_games.BetaWordle()
        await game.start(ctx)




    @game.command(
        aliases = ['memory', 'memorygame'],
        usage = "send_messages",
        brief = 'None',
        description = "Test your memory",
        help = "```Example: memorygame```")
    async def memory_game(self, ctx: commands.Context[commands.Bot]):

        game = button_games.MemoryGame()
        await game.start(ctx)

    @game.command(
        aliases = ['rock', 'paper', 'scissors'],
        usage = "send_messages",
        brief = 'None',
        description = "Play a game of rps",
        help = "```Example: rps```")
    async def rps(
        self, ctx: commands.Context[commands.Bot], player: discord.User = None
    ):

        game = button_games.BetaRockPaperScissors(
            player
        )  # defaults to playing with bot if player = None
        await game.start(ctx)


    @game.command(
        name="connect4",
        aliases = ['c4'],
        usage = "send_messages",
        description = "Play a game of connect four with someone",
        brief = 'user',
        help = "```Syntax: c4 [user]\nExample: c4 @jacob```")
    async def connect4(self, ctx: commands.Context[commands.Bot], member: discord.User):
        game = games.ConnectFour(
            red=ctx.author,
            blue=member,
        )
        await game.start(ctx)

    @game.command(
        name="typerace",
        aliases = ['typeracer', 'tr', 'type'],
        usage = "send_messages",
        brief = 'None',
        description = "Test your typing speed",
        help = "```Example: tr```")
    async def typerace(self, ctx: commands.Context[commands.Bot]):
        game = games.TypeRacer()
        await game.start(ctx, timeout=30)


async def setup(bot):
    await bot.add_cog(games2(bot))