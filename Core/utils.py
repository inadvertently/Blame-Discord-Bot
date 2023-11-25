import copy, os, discord, aiohttp, asyncio, random, arrow,time, io, colorgram,json,sys, time, logging
import motor.motor_asyncio, regex, re
from itertools import cycle
from unittest import result
from Core import exceptions
from discord.ext import commands
from discord.utils import get
import button_paginator as pg
from io import BytesIO
from PIL import Image
from typing import Callable, Optional
logger=logging.getLogger(__name__)


themes = {}
async def get_theme(self, bot=None, guild=None):
    try:
        search = themes[guild]
        data = search['color']
    except KeyError:
        data = "3c91bd"
    return data


#async def require_chunked(guild: discord.Guild):
    #if guild is not None and not guild.chunked:
       #start_time = time()
        #await guild.chunk(cache=True)
       # logger.info(
       #     f"Chunked [{guild}] with {guild.member_count} members in {time() - start_time:.2f} seconds"
       #)

async def test_vars(ctx, user, params):
    if "{user}" in params:
        params = params.replace("{user}", str(user))
    if "{user.mention}" in params:
        params = params.replace("{user.mention}", str(user.mention))
    if "{user.name}" in params:
        params = params.replace("{user.name}", str(user.name))
    if "{user.avatar}" in params:
        params = params.replace("{user.avatar}", str(user.avatar.url))
    if "{user.joined_at}" in params:
        params = params.replace("{user.joined_at}", discord.utils.format_dt(user.joined_at, style="R"))
    if "{user.discriminator}" in params:
        params = params.replace("{user.discriminator}", str(user.discriminator))

    if "{guild.name}" in params:
        params = params.replace("{guild.name}", str(ctx.guild.name))
    if "{guild.count}" in params:
        params = params.replace("{guild.count}", str(user.guild.member_count))
    if "{guild.id}" in params:
        params = params.replace("{guild.id}", str(user.guild.id))
    if "{guild.created_at}" in params:
        params = params.replace("{guild.created_at}", discord.utils.format_dt(user.guild.created_at, style="R"))
    if "{guild.boost_count}" in params:
        params = params.replace("{guild.boost_count}", str(user.guild.premium_subscription_count))
    if "{guild.boost_tier}" in params:
        params = params.replace("{guild.boost_tier}", str(user.guild.premium_tier))
    if "{guild.icon}" in params:
        params = params.replace("{guild.icon}", str(user.guild.icon.url))
    return params

async def welcome_vars(user, params):
    if "{user}" in params:
        params = params.replace("{user}", str(user))
    if "{user.mention}" in params:
        params = params.replace("{user.mention}", str(user.mention))
    if "{user.name}" in params:
        params = params.replace("{user.name}", str(user.name))
    if "{user.avatar}" in params:
        params = params.replace("{user.avatar}", str(user.avatar.url))
    if "{user.joined_at}" in params:
        params = params.replace("{user.joined_at}", discord.utils.format_dt(user.joined_at, style="R"))
    if "{user.discriminator}" in params:
        params = params.replace("{user.discriminator}", str(user.discriminator))

    if "{guild.name}" in params:
        params = params.replace("{guild.name}", str(user.guild.name))
    if "{guild.count}" in params:
        params = params.replace("{guild.count}", str(user.guild.member_count))
    if "{guild.id}" in params:
        params = params.replace("{guild.id}", str(user.guild.id))
    if "{guild.created_at}" in params:
        params = params.replace("{guild.created_at}", discord.utils.format_dt(user.guild.created_at, style="R"))
    if "{guild.boost_count}" in params:
        params = params.replace("{guild.boost_count}", str(user.guild.premium_subscription_count))
    if "{guild.boost_tier}" in params:
        params = params.replace("{guild.boost_tier}", str(user.guild.premium_tier))
    if "{guild.icon}" in params:
        params = params.replace("{guild.icon}", str(user.guild.icon.url))
    return params

async def bleed_content(ctx, params):
    msg = params
    for field in bleed_parts(params):
        data = bleed_field(field)

        if data.get('content'):
            msg = data['content']
        else:
            msg = None
    return msg

async def to_content(ctx, params):
    msg = params
    for field in get_parts(params):
        data = parse_field(field)

        if data.get('content'):
            msg = data['content']
        else:
            msg = None
    return msg

async def to_embed(ctx, params):
    '''Actually formats the parsed parameters into an Embed'''
    em = discord.Embed()

    if not params.count('('):
        if not params.count(')'):
            em.description = params

    for field in get_parts(params):
        data = parse_field(field)

        color = data.get('color') or data.get('colour')
        if color == 'random':
            em.color = random.randint(0, 0xFFFFFF)
        elif color == 'chosen':
            maybe_col = os.environ.get('COLOR')
            if maybe_col:
                raw = int(maybe_col.strip('#'), 16)
                return discord.Color(value=raw)
            else:
                return await ctx.send('color error')

        elif color:
            color = int(color.strip('#'), 16)
            em.color = discord.Color(color)

        if data.get('description'):
            em.description = data['description']

        if data.get('desc'):
            em.description = data['desc']

        if data.get('title'):
            em.title = data['title']

        if data.get('content'):
            message = data['content']

        if data.get('url'):
            em.url = data['url']

        author = data.get('author')
        icon, url = data.get('icon'), data.get('url')

        if author:
            em._author = {'name': author}
            if icon:
                em._author['icon_url'] = icon
            if url:
                em._author['url'] = url

        field, value = data.get('field'), data.get('value')
        inline = False if str(data.get('inline')).lower() == 'false' else True
        if field and value:
            em.add_field(name=field, value=value, inline=inline)

        if data.get('thumbnail'):
            em._thumbnail = {'url': data['thumbnail']}

        if data.get('image'):
            em._image = {'url': data['image']}

        if data.get('footer'):
            em._footer = {'text': data.get('footer')}
            if data.get('icon'):
                em._footer['icon_url'] = data.get('icon')

        if 'timestamp' in data.keys() and len(data.keys()) == 1:
            em.timestamp = ctx.message.created_at

    return em

async def bleed_embed(ctx, params):
    '''Actually formats the parsed parameters into an Embed'''
    em = discord.Embed()

    if not params.count('{'):
        if not params.count('}'):
            em.description = params

    for field in bleed_parts(params):
        data = bleed_field(field)

        color = data.get('color') or data.get('colour')
        if color == 'random':
            em.color = random.randint(0, 0xFFFFFF)
        elif color == 'chosen':
            maybe_col = os.environ.get('COLOR')
            if maybe_col:
                raw = int(maybe_col.strip('#'), 16)
                return discord.Color(value=raw)
            else:
                return await ctx.send('color error')

        elif color:
            color = int(color.strip('#'), 16)
            em.color = discord.Color(color)

        if data.get('description'):
            em.description = data['description']

        if data.get('desc'):
            em.description = data['desc']

        if data.get('title'):
            em.title = data['title']

        if data.get('content'):
            message = data['content']

        if data.get('url'):
            em.url = data['url']

        author = data.get('author')
        icon, url = data.get('icon'), data.get('url')

        if author:
            em._author = {'name': author}
            if icon:
                em._author['icon_url'] = icon
            if url:
                em._author['url'] = url

        field, value = data.get('field'), data.get('value')
        inline = False if str(data.get('inline')).lower() == 'false' else True
        if field and value:
            em.add_field(name=field, value=value, inline=inline)

        if data.get('thumbnail'):
            em._thumbnail = {'url': data['thumbnail']}

        if data.get('image'):
            em._image = {'url': data['image']}

        if data.get('footer'):
            em._footer = {'text': data.get('footer')}
            if data.get('icon'):
                em._footer['icon_url'] = data.get('icon')

        if 'timestamp' in data.keys() and len(data.keys()) == 1:
            em.timestamp = ctx.message.created_at

    return em

def bleed_parts(string):
    '''
    Splits the sections of the embed command
    '''
    for i, char in enumerate(string):
        if char == "{":
            ret = ""
            while char != "}":
                i += 1
                char = string[i]
                ret += char
            yield ret.rstrip('}')

def bleed_field(string):
    '''
    Recursive function to get all the key val
    pairs in each section of the parsed embed command
    '''
    ret = {}

    parts = string.split(':')
    key = parts[0].strip().lower()
    val = ':'.join(parts[1:]).strip()

    ret[key] = val

    if '&&' in string:
        string = string.split('&&')
        for part in string:
            ret.update(bleed_field(part))
    print(ret)
    return ret

def get_parts(string):
    '''
    Splits the sections of the embed command
    '''
    for i, char in enumerate(string):
        if char == "(":
            ret = ""
            while char != ")":
                i += 1
                char = string[i]
                ret += char
            yield ret.rstrip(')')

def parse_field(string):
    '''
    Recursive function to get all the key val
    pairs in each section of the parsed embed command
    '''
    ret = {}

    parts = string.split(':')
    key = parts[0].strip().lower()
    val = ':'.join(parts[1:]).strip()

    ret[key] = val

    if '&&' in string:
        string = string.split('&&')
        for part in string:
            ret.update(parse_field(part))
    print(ret)
    return ret




async def get_emoji(ctx, argument, fallback=None):
    """
    :param argument : name, id, message representation
    :param fallback : return this if not found
    :returns        : discord.Emoji | discord.PartialEmoji
    """
    if argument is None:
        return fallback
    try:
        return await commands.EmojiConverter().convert(ctx, argument)
    except commands.errors.BadArgument:
        try:
            return await commands.PartialEmojiConverter().convert(ctx, argument)
        except commands.errors.BadArgument:
            return fallback

async def index_user(self, bot, author):
    db = bot.db['lastfm']
    try:
        data = await db.find_one({"user_id": author})
    except Exception as e:
        print(e); pass
    index_entries = await db.count_documents({ "user_id": author })
    if index_entries:
        return data['lastfm_username']

async def get_prefix(self, bot, ctx):
    db = bot.db["prefix"]
    data = await db.find_one({ "guild_id": ctx.guild.id })
    if data: #if in db
      pref = data['prefix']
      return pref

async def api_req(self, params, ignore_errors=False):
    #Retrieving json data from the api
    url = "http://ws.audioscrobbler.com/2.0/"
    params["api_key"] = os.environ.get("LASTFM_TOKEN")
    params["format"] = "json"
    tries = 0 
    max_tries = 2
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                try:
                    content = await response.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    if ignore_errors:
                        return None
                    text = await response.text()
                    raise exceptions.LastFMError(error_code=response.status, message=text)

                if content is None:
                    raise exceptions.LastFMError(
                        error_code=408,
                        message="Could not connect to LastFM",
                    )
                if response.status == 200 and content.get("error") is None:
                    return content
                if int(content.get("error")) == 8:
                    tries += 1
                    if tries < max_tries:
                        continue

                if ignore_errors:
                    return None
                raise exceptions.LastFMError(
                    error_code=content.get("error"),
                    message=content.get("message"),
                )

async def get_commits(author, repository):
    url = f"https://api.github.com/repos/{author}/{repository}/commits"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={'accept': 'application/vnd.github.v3.raw', 'authorization': os.environ.get("GITHUB_TOKEN")
            }) as response:
            data = await response.json()
    return data





def getheaders(token=None, content_type="application/json"):
    headers = {
        "Content-Type": content_type,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
    }
    if token:
        headers.update({"Authorization": token})
    return headers

def getHeaders(token=None, content_type="application/json"):
    headers = {
        "Content-Type": content_type,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
    }
    if token:
        headers.update({"Authorization": token})
    return headers

#async def page_switcher(ctx, pages):
   # """
    #:param ctx   : Context
   # :param pages : List of embeds to use as pages
   # """
   # embeds=pages
   # paginator = pg.Paginator(ctx.bot, embeds, ctx)
   # paginator.add_button('prev', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.blurple)
   # #paginator.add_button('delete', label='Close the paginator', emoji='⏹')
   # paginator.add_button('next', emoji='<:right:934237462660788304>', style=discord.ButtonStyle.blurple)
  #  await paginator.start()



async def page_switcher(
    ctx: commands.Context,
    pages: list,
    send_to: Optional[discord.abc.Messageable] = None,
):
    """
    :param ctx   : Context
    :param pages : List of embeds to use as pages
    """
    if len(pages) == 1:
        return await (send_to or ctx).send(embed=pages[0])

    page_iterator = TwoWayIterator(pages)

    # add all page numbers
    for i, page in enumerate(page_iterator.items, start=1):
        old_footer = page.footer.text
        page.set_footer(
            text=f"{i}/{len(page_iterator.items)}"
            + (f" | {old_footer}" if old_footer is not None else "")
        )

    #msg = await (send_to or ctx).send(embed=page_iterator.current())

    paginator = pg.Paginator(ctx.bot, pages, ctx)
    paginator.add_button('prev', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.blurple)
    #paginator.add_button('delete', label='Close the paginator', emoji='⏹')
    paginator.add_button('next', emoji='<:right:934237462660788304>', style=discord.ButtonStyle.blurple)
    await paginator.start()

async def get_color(ctx, argument, fallback=None):
    if argument is None:
        return fallback
    try:
        return await commands.ColourConverter().convert(ctx, argument)
    except commands.errors.BadArgument:
        return fallback

async def scrape_np_to_yt(self, username):
    data = await api_req(self, params=
        {"user": username, "method": "user.getrecenttracks"}, ignore_errors=True)
    if data is None:
        return None
    artist = data['recenttracks']['track'][0]['artist']['#text']
    track = data['recenttracks']['track'][0]['name']
    params = {'search_query': artist+track}
    async with aiohttp.ClientSession() as s:
        async with s.get(f"http://www.youtube.com/results?",  params=params) as html_content:
            a = await html_content.text()	
            search_results = re.findall(r'\/watch\?v=([a-zA-Z0-9_-]{11})',a)
            msgs = []
            for i in search_results:
                msg = f'https://youtube.com/watch?v={i}'
                msgs.append(msg)
    return msgs[1]

async def get_cover(self, username):
    data = await api_req(self, params=
        {"user": username, "method": "user.getrecenttracks"}, ignore_errors=True)
    if data is None:
        return None
    image_url = data["recenttracks"]["track"][0]["image"][-1]["#text"]
    image_hash = image_url.split("/")[-1].split(".")[0]
    big_image_url = self.cover_base_urls[4].format(image_hash)
    artist_name = data["recenttracks"]["track"][0]["artist"]["#text"]
    album_name = data["recenttracks"]["track"][0]["album"]["#text"]
    async with aiohttp.ClientSession() as session:
        async with session.get(big_image_url) as response:
            unhash = io.BytesIO(await response.read())
            

async def now_playing(self, username, avatar):
    data = await api_req(self, params=
        {"user": username, "method": "user.getrecenttracks"}, ignore_errors=True)
    if data is None:
        return None

    track = data['recenttracks']['track'][0]['name']
    url = data['recenttracks']['track'][0]['url']
    album = data['recenttracks']['track'][0]['album']['#text']
    img = data['recenttracks']['track'][0]['image'][-1]['#text']
    artist = data['recenttracks']['track'][0]['artist']['#text']

    albumdata = await api_req(self, params=
        {"user": username, "method": "album.getinfo", "artist": artist, "album": album}, ignore_errors=True)
    if albumdata is None:
        return None
    albumurl = albumdata['album']['url']
    try:
        albumcount = int(albumdata["album"]["userplaycount"])
    except (KeyError, TypeError):
        albumcount = 0

    trackdata = await api_req(self, params=
        {"user": username, "method": "track.getinfo", "artist": artist, "track": track}, ignore_errors=True)
    if trackdata is None:
        return None
    try:
        count = int(trackdata['track']['userplaycount'])
    except (KeyError, TypeError):
        count = 0

    results = discord.Embed()
        #title = f"{artist} - *{track}*", url=url
    #)
    results.add_field(name="__**Track**__", value=f"**[{track}]({url})**", inline=False)
    results.add_field(name="__**Album**__", value=f"**[{album}]({albumurl})**", inline=True)
    results.set_author(name=username, icon_url=avatar)
    results.set_thumbnail(url=img)
    footer = results.set_footer(text=f"Artist: {artist} ∙ Track plays: {count} ∙ Album plays: {albumcount}")
    try:
        results.colour = int(await color_from_image_url(url=img), 16)
    except:
        results.colour = discord.Color.blurple()
    return results

async def now_playing3(self, username, avatar):
    data = await api_req(self, params=
        {"user": username, "method": "user.getrecenttracks"}, ignore_errors=True)
    if data is None:
        return None

    track = data['recenttracks']['track'][0]['name']
    url = data['recenttracks']['track'][0]['url']
    album = data['recenttracks']['track'][0]['album']['#text']
    img = data['recenttracks']['track'][0]['image'][-1]['#text']
    artist = data['recenttracks']['track'][0]['artist']['#text']

    albumdata = await api_req(self, params=
        {"user": username, "method": "album.getinfo", "artist": artist, "album": album}, ignore_errors=True)
    if albumdata is None:
        return None
    albumurl = albumdata['album']['url']
    try:
        albumcount = int(albumdata["album"]["userplaycount"])
    except (KeyError, TypeError):
        albumcount = 0

    trackdata = await api_req(self, params=
        {"user": username, "method": "track.getinfo", "artist": artist, "track": track}, ignore_errors=True)
    if trackdata is None:
        return None
    try:
        count = int(trackdata['track']['userplaycount'])
    except (KeyError, TypeError):
        count = 0

    results = discord.Embed()
        #title = f"{artist} - *{track}*", url=url
    #)
    results.add_field(name="__**Track**__", value=f"**[{track}]({url})**", inline=True)
    results.add_field(name="__**Album**__", value=f"**[{album}]({albumurl})**", inline=True)
    results.set_author(name=username, icon_url=avatar)
    footer = results.set_footer(text=f"Artist: {artist} ∙ Track plays: {count} ∙ Album plays: {albumcount}")
    try:
        results.colour = int(await color_from_image_url(url=img), 16)
    except:
        results.colour = discord.Color.blurple()
    return results

def count():
    list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    for item in list:
        return item

def format_plays(amount):
    if amount == 1:
        return "play"
    return "plays"

async def topartists(self, username, avatar):
    data = await api_req(self, params=
        {"user": username, "method": "user.gettopartists", 'limit': '10'}, ignore_errors=True)
    if data is None:
        return None

    user_attr = data["topartists"]['@attr']
    artists = data["topartists"]["artist"][0]['name'][:10['amount']]
    if not artists:
        raise exceptions.Info("You haven;t listened to anything yet")



    top_artists_names = [f"{count()}. [**{name['name']}**](https://www.last.fm/api/show/user.getTopArtists) (**{playcount['playcount']}** plays)" for name, playcount in zip(data["topartists"]["artist"], data["topartists"]["artist"])]
    top_artists_string = "\n".join(top_artists_names)

    content = discord.Embed(description=f"{top_artists_string}")
    print(artists)
    return content

async def getnowplaying(self, username):
    playing = {"artist": None, "album": None, "track": None}
    data = await api_req(self, params=
        {"user": username, "method": "user.getrecenttracks", 'limit': 1}, ignore_errors=True)
    if data is None:
        return None
    playing = {"artist": None, "album": None, "track": None}
    try:
        tracks = data["recenttracks"]["track"]
        if tracks:
            playing["artist"] = tracks[0]["artist"]["#text"]
            playing["album"] = tracks[0]["album"]["#text"]
            playing["track"] = tracks[0]["name"]
    except KeyError:
        pass
    print(playing)
    return playing
    pass

async def getnowplaying2(self, username):
    playing = {"artist": None, "album": None, "track": None}
    data = await api_req(self, params=
        {"user": username, "method": "user.getrecenttracks", 'limit': 1}, ignore_errors=True)
    if data is None:
        return None
    try:
        tracks = data["recenttracks"]["track"]
        if tracks:
            playing = tracks[0]["artist"]["#text"]
    except KeyError:
        pass
    print(playing)
    return playing
    pass

def escape_md(s):
    """
    :param s : String to espace markdown from
    :return  : The escaped string
    """
    transformations = {regex.escape(c): "\\" + c for c in ("*", "`", "_", "~", "\\", "||")}

    def replace(obj):
        return transformations.get(regex.escape(obj.group(0)), "")

    pattern = regex.compile("|".join(transformations.keys()))
    return pattern.sub(replace, s)

def displayname(member, escape=True):
    if member is None:
        return None

    name = member.name
    if isinstance(member, discord.Member):
        name = member.nick or member.name

    if escape:
        return escape_md(name)
    return name

async def server_lastfm_usernames(self, ctx):
    ids= []
    usernames =[]
    guild_user_ids = [user.id for user in ctx.guild.members]
    cursor = self.db.find({"user_id": { "$in": guild_user_ids}})
    async for doc in cursor:
        usernames.append(doc['lastfm_username'])
        ids.append(doc['user_id'])
        resp = list(zip(ids, usernames))
    return resp




async def get_userinfo_embed(self, username):
    data = await api_req(self, params=
        {"user": username, "method": "user.getinfo"}, ignore_errors=True)
    if data is None:
        return None

    data2 = await api_req(self, params=
        {"user": username, "method": "user.getrecenttracks", 'limit': '1'}, ignore_errors=True)
    if data2 is None:
        return None

    data3 = await api_req(self, params=
        {"user": username, "method": "user.gettopartists", 'limit': '1'}, ignore_errors=True)
    if data3 is None:
        return None

    data4 = await api_req(self, params=
        {"user": username, "method": "user.gettopalbums", 'limit': '1'}, ignore_errors=True)
    if data3 is None:
        return None


    username = data["user"]["name"]
    playcount = data["user"]["playcount"]
    profile_url = data["user"]["url"]
    profile_pic_url = data["user"]["image"][3]["#text"]
    timestamp = arrow.get(int(data["user"]["registered"]["unixtime"]))

    track_artist = data2['recenttracks']['track'][0]['artist']['#text']
    track = data2['recenttracks']['track'][0]['name']
    image_url = data2['recenttracks']['track'][0]["image"][-1]["#text"]

    top_artist = data3['topartists']['artist'][0]['name']
    artist_playcount = data3['topartists']['artist'][0]['playcount']

    top_album = data4['topalbums']['album'][0]['name']
    top_album_playcount = data4['topalbums']['album'][0]['playcount']


    content = discord.Embed(
        title=f"{username}", url=f"{profile_url}", description=f"Last listened to: **[{track}]({image_url})** by **{track_artist}** "
        + (" `LAST.FM PRO`" if int(data["user"]["subscriber"]) == 1 else "")
    )
    content.add_field(name="Country", value=data["user"]["country"])
    content.add_field(name="Total Scrobbles", value=playcount)
    content.add_field(
        name="Registered",
        value=f"{timestamp.format('DD MMM, YYYY')}",
        inline=True,
    )
    content.set_thumbnail(url=image_url)

    content.add_field(name="Profile", value=f"**[Here]({profile_url})**", inline=True)
    content.add_field(name="Top Artist", value=f"**__{top_artist}__**\n╰ (**{artist_playcount}** *plays*)", inline=True)
    content.add_field(name="Top Album", value=f"**__{top_album}__**\n╰ (**{top_album_playcount}** *plays*)", inline=True)
    
    content.set_thumbnail(url=image_url)
    content.set_footer(text=f"Results found from Last.fm")
    content.colour = 0xb90000

    return content


async def imgpage(ctx, embeds):
    paginator = pg.Paginator(ctx.bot, embeds, ctx)
    if len(embeds) > 1:
        paginator.add_button('prev', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.green)
    #paginator.add_button('delete', label='Close the paginator', emoji='⏹')
        paginator.add_button('next', emoji='<:right:934237462660788304>', style=discord.ButtonStyle.green)
    ##🔢#⏹️
        paginator.add_button('goto', emoji='🔢', style=discord.ButtonStyle.grey)
        paginator.add_button('end', emoji='⏹️', style=discord.ButtonStyle.red)
    await paginator.start()

async def send_as_pages(ctx, content, rows, maxrows=10, maxpages=10):
    embeds=create_pages(content, rows, maxrows, maxpages)
    paginator = pg.Paginator(ctx.bot, embeds, ctx,invoker=ctx.author.id)
    embeds2 = len(embeds)
    if len(embeds) > 1:
        paginator.add_button('prev', emoji='<a:left:921613325920518174>', style=discord.ButtonStyle.blurple)
        paginator.add_button('delete', label='Close the paginator', emoji='⏹')
        paginator.add_button('next', emoji='<:right:921574372693651517>', style=discord.ButtonStyle.blurple)

    await paginator.start()

async def ssend_as_pages(
    ctx: commands.Context,
    content: discord.Embed,
    rows: list,
    maxrows=10,
    maxpages=10,
    send_to: Optional[discord.abc.Messageable] = None,
):
    """
    :param ctx     : Context
    :param content : Base embed
    :param rows    : Embed description rows
    :param maxrows : Maximum amount of rows per page
    :param maxpages: Maximum amount of pages untill cut off
    """
    pages = create_pages(content, rows, maxrows, maxpages)
    if len(pages) > 1:
        await page_switcher(ctx, pages, send_to=send_to)
    else:
        await (send_to or ctx).send(embed=pages[0])

async def page_util(ctx, content, rows, maxrows=10, maxpages=10):
    embeds=create_pages(content, rows, maxrows, maxpages)
    return embeds

async def send_as_page(ctx, content, rows, maxrows=10, maxpages=10):
    embeds=create_pages(content, rows, maxrows, maxpages)
    paginator = pg.Paginator(ctx.bot, embeds, ctx)

    await paginator.start()

async def send_question(ctx, message):
    msg=await ctx.send(embed=discord.Embed(color=0xcb8028, description=f"<:question:1028162879939170314> **{message}**"))
    return msg

async def send_blurple(ctx, message):
    msg=await ctx.send(embed=discord.Embed(color=0x3d91bc, description=f"<:check:1027703035054526475> **{message}**"))
    return msg

async def send_tempblurple(ctx, message):
    msg=await ctx.send(delete_after=5,embed=discord.Embed(color=int(await get_theme(self=ctx, bot=ctx.bot, guild=ctx.guild.id), 16), description=f"**{message}**").set_author(name=ctx.author, icon_url=ctx.author.display_avatar))
    return msg

async def edit_blurple(ctx, message):
    return discord.Embed(color=int(await get_theme(self=ctx, bot=ctx.bot, guild=ctx.guild.id), 16), description=f"<:check:1027703035054526475> **{message}**")

async def send_no(ctx, message):
    msg=await ctx.send(embed=discord.Embed(color=0xA90F25, description=f"<:yy_yno:921559254677200957> {ctx.author.mention}: **{message}**").set_author(name=ctx.author, icon_url=ctx.author.display_avatar))
    return msg

async def send_yes(ctx, message):
    msg=await ctx.send(embed=discord.Embed(color=0x43B581, description=f"<:check:921544057312915498> {ctx.author.mention}: **{message}**").set_author(name=ctx.author, icon_url=ctx.author.display_avatar))
    return msg

async def send_issue(ctx, message):
    msg=await ctx.send(embed=discord.Embed(color=0xf3dd6c, description=f"<:issue:1028165380105052231> {ctx.author.mention}: **{message}**"))
    return msg

async def send_bad(ctx, message):
    await ctx.send(embed=discord.Embed(description=f"<:no:940723951947120650> {ctx.author.mention}: **{message}**", color=int("ff6465", 16)))

async def send_error(ctx, message):
    msg=await ctx.send(embed=discord.Embed(color=0xdc0000, description=f"<:bad:1028153588989571094> {ctx.author.mention}: **{message}**"))
    return msg

async def edit_blurple(ctx, message):
    return discord.Embed(color=int(await get_theme(self=ctx, bot=ctx.bot, guild=ctx.guild.id), 16), description=f"<:check:1027703035054526475> **{message}**")

async def do_removal(ctx, limit, predicate, *, before=None, after=None, message=True):
    if limit > 2000:
        return await ctx.send(f"Too many messages to search given ({limit}/2000)")

    if not before:
        before = ctx.message
    else:
        before = discord.Object(id=before)

    if after:
        after = discord.Object(id=after)

    try:
        deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
    except discord.Forbidden:
        return await ctx.send("I do not have permissions to delete messages.")
    except discord.HTTPException as e:
        return await ctx.send(f"Error: {e} (try a smaller search?)")

    deleted = len(deleted)
    return deleted

def create_pages(content, rows, maxrows=15, maxpages=10):
    """
    :param content : Embed object to use as the base
    :param rows    : List of rows to use for the embed description
    :param maxrows : Maximum amount of rows per page
    :param maxpages: Maximu amount of pages until cut off
    :returns       : List of Embed objects
    """
    pages = []
    content.description = ""
    thisrow = 0
    rowcount = len(rows)
    for row in rows:
        thisrow += 1
        if len(content.description) + len(row) < 2000 and thisrow < maxrows + 1:
            content.description += f"\n{row}"
            rowcount -= 1
        else:
            thisrow = 1
            if len(pages) == maxpages - 1:
                content.description += f"\n*+ {rowcount} more entries...*"
                pages.append(content)
                content = None
                break

            pages.append(content)
            content = copy.deepcopy(content)
            content.description = f"{row}"
            rowcount -= 1

    if content is not None and not content.description == "":
        pages.append(content)

    return pages
 

async def command_group_help(ctx):
    await ctx.send_help(ctx.command or ctx.command.root_parent.name)

async def command_help(ctx):
    #wait ctx.send_help(ctx.command)
    if ctx.command.root_parent:
        cmd=ctx.command.root_parent
    else:
        cmd=ctx.command
    count=0
    counter=0
    embedss=[]
    for command in cmd.walk_commands():
        counter+=1
    for command in cmd.walk_commands():
        for command in commands.walk_commands():  # iterate through all of the command's parents/subcommands
            if command.parents[0] == commands:
                embedss=[]
                count += 1
                emb = discord.Embed(color=int(await get_theme(self=ctx, bot=ctx.bot, guild=ctx.guild.id), 16))
                emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
                if command.brief:
                    embedss.append(emb)
                    emb.add_field(name="⚠️ Parameters", value=command.brief)
                    emb.set_footer(text="Aliases: " + ", ".join(command.aliases)+f" ・ Module: {command.cog_name}.py ・ Entry: ({count}/{counter} entries)") 
                if command.usage:
                    emb.add_field(name="🔒 Permissions", value=command.usage)
                if command.description:
                    emb.title=f"Command: {command.qualified_name}"
                    emb.description=command.description
                if command.help:
                    emb.add_field(name="📲 Usage", value=command.help, inline=False)
                    emb.title=f"Command: {command.qualified_name}"
        paginator = pg.Paginator(ctx.bot, embedss, ctx)
        if len(embedss) > 1:
            paginator.add_button('prev', emoji='<:left:934237439772483604>', style=discord.ButtonStyle.blurple)
            paginator.add_button('next', emoji='<:right:934237462660788304>', style=discord.ButtonStyle.blurple)
        await paginator.start()


def ordinal(n):
    """Return number with ordinal suffix eg. 1st, 2nd, 3rd, 4th..."""
    return str(n) + {1: "st", 2: "nd", 3: "rd"}.get(4 if 10 <= n % 100 < 20 else n % 10, "th")

async def get_artist_image(self, artist):
    image_life = 604800  # 1 week
    cached = await self.bot.db.execute(
        "SELECT image_hash, scrape_date FROM artist_image_cache WHERE artist_name = %s",
        artist,
        one_row=True,
    )



async def send_command_help(ctx):
    """Sends default command help"""
    await ctx.send_help(ctx.invoked_subcommand or ctx.command)

async def get_user(ctx, argument, fallback=None):
    if argument is None:
        return fallback
    try:
        return await commands.UserConverter().convert(ctx, argument)
    except commands.errors.BadArgument:
        return fallback


async def get_member(ctx, argument, fallback=None, try_user=False):
    if argument is None:
        return fallback
    try:
        return await commands.MemberConverter().convert(ctx, argument)
    except commands.errors.BadArgument:
        if try_user:
            return await get_user(ctx, argument, fallback)
        return fallback


async def get_textchannel(ctx, argument, fallback=None, guildfilter=None):
    if argument is None:
        return fallback
    if guildfilter is None:
        try:
            return await commands.TextChannelConverter().convert(ctx, argument)
        except commands.errors.BadArgument:
            return fallback
    else:
        result = discord.utils.find(
            lambda m: argument in (m.name, m.id), guildfilter.text_channels
        )
        return result or fallback


async def get_role(ctx, argument, fallback=None):
    if argument is None:
        return fallback
    try:
        return await commands.RoleConverter().convert(ctx, argument)
    except commands.errors.BadArgument:
        return fallback


async def get_color(ctx, argument, fallback=None):
    if argument is None:
        return fallback
    try:
        return await commands.ColourConverter().convert(ctx, argument)
    except commands.errors.BadArgument:
        return fallback


async def get_emoji(ctx, argument, fallback=None):
    if argument is None:
        return fallback
    try:
        return await commands.EmojiConverter().convert(ctx, argument)
    except commands.errors.BadArgument:
        try:
            return await commands.PartialEmojiConverter().convert(ctx, argument)
        except commands.errors.BadArgument:
            return fallback 



def rgb_to_hex(rgb):
    r, g, b = rgb

    def clamp(x):
        return max(0, min(x, 255))

    return "{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))

async def color_from_image_url(url, fallback="E74C3C", return_color_object=False):
    if url.strip() == "":
        return fallback
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                image = Image.open(BytesIO(await response.read()))
                colors = colorgram.extract(image, 1)
                dominant_color = colors[0].rgb

        if return_color_object:
            return dominant_color
        return rgb_to_hex(dominant_color)
    except Exception as e:
        print(e)
        return fallback


def stringfromtime(t, accuracy=4):
    """
    :param t : Time in seconds
    :returns : Formatted string
    """
    m, s = divmod(t, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    components = []
    if d > 0:
        components.append(f"{int(d)} day" + ("s" if d != 1 else ""))
    if h > 0:
        components.append(f"{int(h)} hour" + ("s" if h != 1 else ""))
    if m > 0:
        components.append(f"{int(m)} minute" + ("s" if m != 1 else ""))
    if s > 0:
        components.append(f"{int(s)} second" + ("s" if s != 1 else ""))

    return " ".join(components[:accuracy])

class TwoWayIterator:
    """Two way iterator class that is used as the backend for paging"""

    def __init__(self, list_of_stuff, loop=False):
        self.items = list_of_stuff
        self.loop = loop
        self.index = 0

    def next(self):
        if self.index == len(self.items) - 1:
            if self.loop:
                self.index = -1
            else:
                return None
        self.index += 1
        return self.items[self.index]

    def previous(self):
        if self.index == 0:
            if self.loop:
                self.index = len(self.items)
            else:
                return None
        self.index -= 1
        return self.items[self.index]

    def current(self):
        return self.items[self.index]
