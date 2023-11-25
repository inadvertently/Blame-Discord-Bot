from TTApi import TikTokApi


tiktok = TikTokApi()

music_data = tiktok.music.get_music_info("7119885743854111493")

print(f"""
ID: {music_data["id_str"]}
TITLE: {music_data["title"]}
MUSIC_LENGTH: {music_data["duration"]}s
PLAY_URL: {music_data["play_url"]["url_list"][0]}
""")