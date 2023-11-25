from TTApi import TikTokApi

tiktok = TikTokApi(debug=True)


video_ids = []
first_page = tiktok.music.get_videos_by_music("7080950666059646978", cursor="0") # starts at 0
second_page = tiktok.music.get_videos_by_music("7080950666059646978", cursor="20") # increases by count, default count is 20


for video in first_page["videos"]:
    print(video["video_id"])
    
for video in second_page["videos"]:
    print(video["video_id"])