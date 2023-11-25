import discord, os,time, socket, os,logging,asyncio, motor.motor_asyncio, Core.help as _init, db.database as connections
from discord.ext import commands
from datetime import datetime as dt
from colorama import Fore as f
from cogs.voicemaster import PersistentView
from aiohttp import AsyncResolver, ClientSession, TCPConnector
from dotenv import load_dotenv
load_dotenv()

class blameInitiator(commands.AutoShardedBot):
	def __init__(self):
		self.global_cd = commands.CooldownMapping.from_cooldown(3, 5, commands.BucketType.member)
		self.start_time = time.time()
		super().__init__(command_prefix=connections.getprefix,help_command = _init.MyHelp(),case_insensitive = True,intents=discord.Intents().all(),activity = discord.Game(name="Experiments"))

    
client = blameInitiator()
client.owner_ids = os.environ.get("BOT_OWNER_ID")
os.environ["JISHAKU_NO_UNDERSCORE"] = "true"

class MyBot(commands.Bot):
		async def is_owner(self, user: discord.User):
				if user.id in client.owner_ids:  # Implement your own conditions here
						return True
				return await super().is_owner(user)

@client.event
async def on_message_edit(before, after):
    await client.process_commands(after)
    
@client.event
async def on_ready():
    await load_extensions()

@client.check
async def cooldown_check(ctx):
	if str(ctx.invoked_with).lower() == "help":
		return True
	bucket = client.global_cd.get_bucket(ctx.message)
	retry_after = bucket.update_rate_limit()
	if retry_after:
		raise commands.CommandOnCooldown(bucket, retry_after, commands.BucketType.member)
	return True

@client.check
async def command_status(ctx):
    db = client.db['commandStatus']
    fetchGuild = await db.find_one({'guild_id': ctx.guild.id})
    if fetchGuild:
        status = fetchGuild['disabled']
        if str(ctx.command) in status:
            await ctx.send(embed=discord.Embed(description=f"<:SystemMessageWarn:1039319472026177676> {ctx.author.mention}: This command is **disabled** in this **server**", color=0xfaa61b), delete_after=8)
            return False
        else: return True
    else: return True


async def load_extensions():
    folders = []
    for i in os.listdir("cogs"):
        if i == "__pycache__": pass
        elif i in folders: 
            for x in os.listdir(f"cogs/{i}"):
                if x == "__pycache__": pass
                else:
                    cog = f"cogs.{i}.{x[:-3]}"
                    try:
                        await client.load_extension(cog)
                        logging.basicConfig(
                                level=logging.INFO,
                                format=f"{f.LIGHTRED_EX}[{f.RESET}{f.BLUE}%(asctime)s{f.RESET}{f.LIGHTRED_EX}]{f.RESET} {f.GREEN}->{f.RESET} {f.LIGHTCYAN_EX}%(message)s{f.RESET}",
                                datefmt="%H:%M:%S",
                        )
                        print(f"{f.LIGHTRED_EX}[{f.RESET}{f.BLUE}(Successfully Initiated){f.RESET}{f.LIGHTRED_EX}]{f.RESET} {f.GREEN}->{f.RESET} {f.LIGHTGREEN_EX}{cog}{f.RESET}")
                    except Exception as e:
                        print(f"{f.YELLOW}->{f.RESET} {f.LIGHTRED_EX}Failed to load{f.RESET} {f.BLUE}->{f.RESET} {f.YELLOW}{cog}{f.RESET} Error: {f.RED}{e}{f.RESET}")
        else:
            cog = f"cogs.{i[:-3]}"
            try:
                await client.load_extension(cog)
                print(f"{f.LIGHTRED_EX}[{f.RESET}{f.BLUE}(Successfully Initiated){f.RESET}{f.LIGHTRED_EX}]{f.RESET} {f.GREEN}->{f.RESET} {f.LIGHTGREEN_EX}{cog}{f.RESET}")
            except Exception as e:
                print(f"{f.YELLOW}->{f.RESET} {f.LIGHTRED_EX}Failed to load{f.RESET} {f.BLUE}->{f.RESET} {f.YELLOW}{cog}{f.RESET} Error: {f.RED}{e}{f.RESET}")
    await client.load_extension('jishaku') 

async def main():
    async with ClientSession(connector=TCPConnector(resolver=AsyncResolver(), family=socket.AF_INET)) as http_session:
            client.connection = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGODB_URI"))
            client.db = client.connection.get_database(os.environ.get("DATABASE"))
            client.add_view(PersistentView(bot=client))
            client.http_session = http_session
            token = os.environ.get("DISCORD_TOKEN")
            logging.basicConfig(
                    level=logging.INFO,
                    format=f"{f.LIGHTRED_EX}[{f.RESET}{f.BLUE}%(asctime)s{f.RESET}{f.LIGHTRED_EX}]{f.RESET} {f.GREEN}->{f.RESET} {f.LIGHTCYAN_EX}%(message)s{f.RESET}",
                    datefmt="%H:%M:%S",
            )
            await client.start(token)

asyncio.run(main()) 