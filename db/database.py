import motor.motor_asyncio, discord, aiohttp, asyncio
from discord.ext import commands

#fetching collection 1
prefixes = {}
default_prefix = ';'


async def getprefix(client, message):
  try:
    db=client.db["prefix"]
    if message.guild == None: #checking if pm
      return commands.when_mentioned_or(default_prefix)(client, message) #retunrning the normal prefix
    try:
      return commands.when_mentioned_or(prefixes[message.guild.id])(client, message) #see if guild in chache
    except KeyError:
      data = await db.find_one({ "guild_id": message.guild.id }) #if not, then we pull from db
      if data: #if in db
        pref = data['prefix']
        struct = prefixes[message.guild.id]=pref #cache it
        return commands.when_mentioned_or(struct)(client, message)
      else: #if not
          await db.insert_one({ #insert it
              "guild_id": message.guild.id,
              "prefix": f"{default_prefix}"
          })
          prefixes[message.guild.id] = default_prefix #cache it
          return commands.when_mentioned_or(prefixes[message.guild.id])(client,message)
  except:
    pass





