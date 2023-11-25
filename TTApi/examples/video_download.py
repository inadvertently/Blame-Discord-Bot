from TTApi import TikTokApi


tiktok = TikTokApi(debug=True)

tiktok.video.download_video("https://www.tiktok.com/t/ZTRf85djY/", watermark=True) # Watermarked
tiktok.video.download_video("https://vm.tiktok.com/ZMNnX3Q4q/", watermark=False) # No watermark