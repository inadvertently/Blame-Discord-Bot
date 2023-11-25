
class Music:
    def __init__(self, api):
        self.api = api
        
    def get_music_info(self, music_id, region="US"):
        # This endpoint requires device_id as a param
        music_info = self.api.session.get(f"https://api2-19-h2.musical.ly/aweme/v1/music/detail/?music_id={music_id}&click_reason=0&os_api=25&device_type=SM-G973N&ssmix=a&manifest_version_code=2019090808&dpi=320&carrier_region={region}&uoo=0&region={region}&carrier_region_v2=310&app_name=musical_ly&version_name=13.0.3&timezone_offset=7200&ts=1661162913&ab_version=13.0.3&residence={region}&pass-route=1&pass-region=1&is_my_cn=0&current_region={region}&ac2=wifi&app_type=normal&ac=wifi&channel=googleplay&update_version_code=2019090808&device_platform=android&build_number=13.0.3&locale=en&version_code=130003&timezone_name=Africa%2FHarare&sys_region={region}&device_id=6648868528752936454&app_language=en&resolution=1080*1920&device_brand=samsung&language=en&os_version=7.1.2&aid=1233")
        res = music_info.json()
        return res["music_info"]

    
    def get_videos_by_music(self, music_id, cursor="0", count="20", region="US"):
        music_videos = self.api.session.get(f"https://api2-19-h2.musical.ly/aweme/v1/music/aweme/?music_id={music_id}&count={count}&cursor={cursor}&type=0&click_reason=0&os_api=25&device_type=SM-G973N&ssmix=a&manifest_version_code=2019090808&dpi=320&carrier_region={region}&uoo=0&region={region}&carrier_region_v2=310&app_name=musical_ly&version_name=13.0.3&timezone_offset=7200&ts=1661162913&ab_version=13.0.3&residence={region}&pass-route=1&pass-region=1&is_my_cn=0&current_region={region}&ac2=wifi&app_type=normal&ac=wifi&channel=googleplay&update_version_code=2019090808&device_platform=android&build_number=13.0.3&locale=en&version_code=130003&timezone_name=Africa%2FHarare&sys_region={region}&device_id=6648868528752936454&app_language=en&resolution=1080*1920&device_brand=samsung&language=en&os_version=7.1.2&aid=1233")
        res = music_videos.json()
        videos = {"videos": []}
        music_info = res["aweme_list"][0]["music"]
        videos["music"] = {
            "artists": music_info["artists"], # Most likely None
            "music_id": music_info["id_str"],
            "music_length": music_info["duration"],
            "author": music_info["author"],
            "title": music_info["title"],
            "play_url": music_info["play_url"]["uri"],
            "music_id": music_info["mid"],
            "cover": music_info["cover_large"]["url_list"][0]
        }
        for video in res["aweme_list"]:
            videos["videos"].append(self.api.video.video_data_formatter(video))
        return videos        