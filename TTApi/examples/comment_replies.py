from TTApi import TikTokApi
import requests

tiktok = TikTokApi()

# page 1 replies
replies = tiktok.comment.get_replies("7126994194535924485", count="3")

for reply in replies:
    print(reply["text"])

# page 2 replies
replies = tiktok.comment.get_replies("7126994194535924485", count="3", cursor="3")

for reply in replies:
    print(reply["text"])