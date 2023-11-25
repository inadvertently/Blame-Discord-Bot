import discord, motor, asyncio, Core.utils as util, Core.confirm as cop_is_gae, typing
from discord.ext import commands
from typing import List
import discord.ui
from Core import utils as util
from datetime import datetime
from Core.utils import get_theme


class autoResponsEEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db['autoResponder']
        self._cd = commands.CooldownMapping.from_cooldown(1, 6.0, commands.BucketType.member)

    def get_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
        """Returns the ratelimit left"""
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()


    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.guild is None:
                return
            if message.author == self.bot.user:
                return
            if message.author.bot:
                return
            ctx=await self.bot.get_context(message)
            check = await self.db.count_documents({ "guild_id": message.guild.id })
            mention=f"<@!{self.bot.user.id}>"
            mention2=f"<@{self.bot.user.id}>"
            if message.content == mention or message.content == mention2:
                ratelimit = self.get_ratelimit(message)
                if ratelimit is None:
                    prefix=await util.get_prefix(self=ctx, bot=self.bot, ctx=ctx)
                    try:
                        return await message.channel.send(embed=discord.Embed(color=int(await get_theme(self, bot=self.bot, guild=ctx.guild.id), 16), description=f":mag: Prefix = **{prefix}**"))
                    except:
                        pass
                else:
                    return
            if check:
                check_existing = self.db.find({ "guild_id": message.guild.id })
                for trigger in await check_existing.to_list(length=20):
                    found = trigger["trigger"]
                    if found in message.content.lower():
                        ratelimit = self.get_ratelimit(message)
                        if ratelimit is None:
                            response = trigger['response']
                            channel = message.channel
                            try:
                                return await channel.send(response)
                            except Exception as e: 
                                print (e)
                        else:
                            return

            else:
                return
        except:
            pass; return

                


async def setup(bot):
    await bot.add_cog(autoResponsEEvent(bot))