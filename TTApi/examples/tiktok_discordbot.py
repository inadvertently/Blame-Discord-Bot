from ast import Bytes
from TTApi import TikTokApi
from io import BytesIO
import discord


tiktok = TikTokApi()
bot_token = ""
prefix = ";"
class tiktokbot(discord.Client):
    async def on_connect(self):
       print("TikTok Bot connected.")
       
    async def on_message(self, msg):
        if msg.author.bot: return
        if not msg.content.startswith(prefix): return
        args = msg.content[1:].split(" ")
        if (args[0] == "tiktok"):
            if len(args) > 1:
                link = args[1]
                video_data = tiktok.parse_video_data(link)
                no_watermark_download = video_data["download_urls"]["no_watermark"]
                video_binary = tiktok.get_video_binary(no_watermark_download)
                bytes_io = BytesIO(video_binary) # discord.py takes this shit for some reason
                embed = discord.Embed()
                embed.description = f'**{video_data["description"]}]**'
                embed.set_author(name="Tiktok by @"+video_data["author"]["username"], icon_url="https://cdn.discordapp.com/emojis/1010602768660181012.png?size=256", url=video_data["video_url"])
                embed.set_footer(text=f"💬 {video_data['stats']['comment_count']} | 👍 {video_data['stats']['likes']} | 🔗 {video_data['stats']['shares']} ({video_data['stats']['views']} views)\n🎵 {video_data['music']['title']} (by {video_data['music']['author']})")
                await msg.channel.send(file=discord.File(fp=bytes_io, filename="tiktok.mp4"), embed=embed)
            else:
                await msg.channel.send(f'Correct usage: `;tiktok <videoID | videoURL>`')



client = tiktokbot()
client.run(bot_token, bot=True)
