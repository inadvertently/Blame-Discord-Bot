import io
import os
import re
import zlib
import logging

import aiohttp
import discord
from discord.ext import commands
import cogs.motorScrape as motors


class SphinxObjectFileReader:
   
    BUFSIZE = 16 * 1024

    def __init__(self, buffer):
        self.stream = io.BytesIO(buffer)

    def readline(self):
        return self.stream.readline().decode("utf-8")

    def skipline(self):
        self.stream.readline()

    def read_compressed_chunks(self):
        decompressor = zlib.decompressobj()
        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self):
        buf = b""
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b"\n")
            while pos != -1:
                yield buf[:pos].decode("utf-8")
                buf = buf[pos + 1 :]
                pos = buf.find(b"\n")


class Docs(commands.Cog, name="Documentation"):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

        self.page_types = {
            "discord.py": "https://discordpy.readthedocs.io/en/latest",
            "latest": "https://discordpy.readthedocs.io/en/latest/",
            "stable": "https://discordpy.readthedocs.io/en/stable/",
            "v1.7.3": "https://discordpy.readthedocs.io/en/v1.7.3/",
            "v1.7.2": "https://discordpy.readthedocs.io/en/v1.7.2/",
            "v1.7.1": "https://discordpy.readthedocs.io/en/v1.7.1/",
            "v1.7.0": "https://discordpy.readthedocs.io/en/v1.7.0",
            "v1.6.0": "https://discordpy.readthedocs.io/en/v1.6.0",
            "legacy": "https://discordpy.readthedocs.io/en/legacy/",
            "async": "https://discordpy.readthedocs.io/en/async/",
            "ja_latest": "https://discordpy.readthedocs.io/ja/latest/",
            "ja_stable": "https://discordpy.readthedocs.io/ja/stable/",
        }

    def finder(self, text, collection, *, key=None, lazy=True):
        suggestions = []
        text = str(text)
        pat = ".*?".join(map(re.escape, text))
        regex = re.compile(pat, flags=re.IGNORECASE)
        for item in collection:
            to_search = key(item) if key else item
            r = regex.search(to_search)
            if r:
                suggestions.append((len(r.group()), r.start(), item))

        def sort_key(tup):
            if key:
                return tup[0], tup[1], key(tup[2])
            return tup

        if lazy:
            return (z for _, _, z in sorted(suggestions, key=sort_key))
        else:
            return [z for _, _, z in sorted(suggestions, key=sort_key)]

    def parse_object_inv(self, stream, url):
    
        result = {}

     
        inv_version = stream.readline().rstrip()

        if inv_version != "# Sphinx inventory version 2":
            raise RuntimeError("Invalid objects.inv file version.")

        stream.readline().rstrip()[11:]
        stream.readline().rstrip()[11:]


        line = stream.readline()
        if "zlib" not in line:
            raise RuntimeError("Invalid objects.inv file, not z-lib compatible.")

        # This code mostly comes from the Sphinx repository.
        entry_regex = re.compile(r"(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)")
        for line in stream.read_compressed_lines():
            match = entry_regex.match(line.rstrip())
            if not match:
                continue

            name, directive, prio, location, dispname = match.groups()
            domain, _, subdirective = directive.partition(":")
            if directive == "py:module" and name in result:

                continue

            if directive == "std:doc":
                subdirective = "label"

            if location.endswith("$"):
                location = location[:-1] + name

            key = name if dispname == "-" else dispname
            prefix = f"{subdirective}:" if domain == "std" else ""

            result[f"{prefix}{key}"] = os.path.join(url, location)

        return result

    async def build_rtfm_lookup_table(self, page_types):
        cache = {}
        for key, page in page_types.items():
            async with aiohttp.ClientSession() as session:
                async with session.get(page + "/objects.inv") as resp:
                    if resp.status != 200:
                        raise RuntimeError(
                            "Cannot build rtfm lookup table, try again later."
                        )

                    stream = SphinxObjectFileReader(await resp.read())
                    cache[key] = self.parse_object_inv(stream, page)

        self._rtfm_cache = cache

    async def do_rtfm(self, ctx, key, obj):
        page_types = self.page_types

        if obj is None:
            await ctx.send(page_types[key])
            return

        if not hasattr(self, "_rtfm_cache"):
            await self.build_rtfm_lookup_table(page_types)

        cache = list(self._rtfm_cache[key].items())

        self.matches = self.finder(obj, cache, key=lambda t: t[0], lazy=False)[:8]

        e = discord.Embed(colour=discord.Color.blurple())
        if len(self.matches) == 0:
            return await ctx.send("Could not find anything. Sorry.")

        e.description = "\n".join(f"[`{key}`]({url})" for key, url in self.matches)
        await ctx.send(embed=e)

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info("I'm ready!")




    @commands.command(
        description="Scrapes documentation and returns a link for d.py latest", hidden=True
    )
    async def rtfm(self, ctx, key: str = None, *, query: str = None):
        if not key or key.lower() not in self.page_types.keys():
            query = query or ""
            key = key or ""

            query = key + query
            key = "discord.py"

        if query is not None:
            if query.lower() == "rtfm":
                await ctx.send('https://discordpy.readthedocs.io/en/stable')

        await self.do_rtfm(ctx, key, query)





async def setup(bot):
    await bot.add_cog(Docs(bot))