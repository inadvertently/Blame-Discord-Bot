import aioredis, asyncio, os
from discord.ext import commands, tasks
from os import environ


class Redis(commands.Cog):
    """For redis."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.pool = None
        self._connect_task = self.bot.loop.create_task(self.connect())
        self.cache_guilds.start()
        self.cache_users.start()

    async def connect(self):
        self.pool = await aioredis.create_redis_pool(os.environ.get("REDIS_SERVER_IP"), password=os.environ.get("REDIS_SERVER_PASSWORD"), encoding='utf-8')

    async def close(self):
        self.pool.close()
        await self.pool.wait_closed()

    async def wait_until_ready(self):
        await self._connect_task

    def cog_unload(self):
        self.bot.loop.create_task(self.close())

    @tasks.loop(minutes=30)
    async def cache_guilds(self):
        guilds = [int(i.id) for i in self.bot.guilds]
        if not await self.bot.redis.lrange('guilds', 0, -1):
            return await self.bot.redis.rpush('guilds', *guilds)
        data = await self.bot.redis.lrange('guilds', 0, -1)
        for i in guilds:
            if not i in data:
                await self.bot.redis.rpush('guilds', i)

    @tasks.loop(hours=24)
    async def cache_users(self):
        users = sum(self.bot.get_all_members())
        if not await self.bot.redis.get('users'):
            await self.bot.redis.set('users', f"{users}")
        else:
            check = int(await self.bot.redis.get('users'))
            await self.bot.redis.set('users', f"{check + sum(self.bot.get_all_members())}")



    @cache_users.before_loop
    async def before_cache_users(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(10)


    @cache_guilds.before_loop
    async def before_cache_guilds(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(10)

        



async def setup(bot: commands.Bot):
    await bot.add_cog(Redis(bot))
