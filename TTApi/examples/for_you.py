from TTApi import TikTokApi

tiktok = TikTokApi(debug=True)

fyp_videos = tiktok.feed.for_you()

for video in fyp_videos:
    tiktok.video.download_video(video["video_url"])