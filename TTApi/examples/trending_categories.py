from TTApi import TikTokApi

tiktok = TikTokApi(debug=True)
trending_categories = tiktok.feed.trending_categories()

for category in trending_categories:
    videos = category["videos"]
    trending_type = category["trending_type"]
    amount_of_videos_under_category = category["video_count"]
    
    if trending_type == "hashtag":
        print(category["hashtag"]) # hashtag info
    elif trending_type == "music":
        print(category["music"]) # music info