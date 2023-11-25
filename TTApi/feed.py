from datetime import datetime
import json
from re import L
import time
from .exceptions import No_Response

class Feed:
    def __init__(self, api):
        self.api = api
        self.trending_types = {
            1: "music",
            0: "hashtag"
        }
        
    def for_you(self, count="6", max_cursor="0", min_cursor="0", region="US", raw_data=False) -> list:
        """_Get videos off the for you page_
        Args:
            count (str, optional): _Amount of videos to return_. Defaults to "6".
            max_cursor (str, optional): _-1 or 0_. Defaults to "0".
            min_cursor (str, optional): _Only seen this be 0_. Defaults to "0".
            region (str, optional): _The region u want the view the fyp of_. Defaults to "US".
            raw_data (bool, optional): _Wether u want the raw data from the videos that it gets off the FYP_. Defaults to False.
        Returns:
            list: _List of dicts containing tiktok videos_
        """
        try:
            pull_type = self.set_pull_type(min_cursor, max_cursor, count)
            _rticket = str(time.time() * 1000).split(".")[0]
            ts = str(time.time()).split(".")[0]
            req_from = self.set_req_from(min_cursor, max_cursor)
            feed_request = self.api.session.get(f"https://api2-19-h2.musical.ly/aweme/v1/feed/?type=0&max_cursor={max_cursor}&min_cursor={min_cursor}&count={count}&{req_from}&volume=0.2&pull_type={pull_type}&ts={ts}&_rticket={_rticket}&address_book_access=1&gps_access=2&os_api=25&device_type=SM-G973N&dpi=320&uoo=0&region={region}&carrier_region={region}&app_name=musical_ly")
            res = feed_request.json()["aweme_list"]
            videos = []
            for vid in res:
                if raw_data:
                    videos.append(vid)
                else:
                    formatted_video_data = self.api.video.video_data_formatter(vid)
                    videos.append(formatted_video_data)
            return videos
        except json.JSONDecodeError as e:
            raise No_Response
    
    def trending(self):
        pass
        
    def trending_categories(self, cursor="0", count="10", region="US", raw=False):
        """Gets the current trending sounds/hashtags in specified region

        Args:
            cursor (str, optional): _Cursor is pagination, cursor 0 will get first page, then the page increases per count._. Defaults to "0".
            count (str, optional): _Amount of categories to get_. Defaults to "10".
            region (str, optional): _Region will determine in what country to get trending categories from_. Defaults to "US".
            raw (bool, optional): _True if you want the raw data from tiktok, this is messy though and you'll have to take time looking through it_. Defaults to False.

        Returns:
            _type_: _description_
        """
        trending_categories_request = self.api.session.get(f"https://api2-19-h2.musical.ly/aweme/v2/category/list/?cursor={cursor}&count={count}&os_api=25&device_type=SM-G973N&ssmix=a&manifest_version_code=2019090808&dpi=320&carrier_region={region}&uoo=0&region={region}&app_name=musical_ly&version_name=13.0.3&is_my_cn=0&ac2=wifi&ac=wifi&app_type=normal&channel=googleplay&build_number=13.0.3&locale=en&sys_region={region}")
        res = trending_categories_request.json()
        if raw:
            return res
        else:
            return self.format_categories(res["category_list"])
                    
    def set_pull_type(self, min_cursor, max_cursor, count):
        if max_cursor and min_cursor == "0":
            return '4'
        if max_cursor == "0" and min_cursor != "0":
            return '2'
        
    def set_req_from(self, min_cursor, max_cursor):
        if min_cursor != "0" and max_cursor == "0":
            return 'req_from'
        else:
            return 'req_from=enter_auto'
    
    def format_categories(self, cat_data) -> list:
        data = []
        for cat in cat_data:
            t = cat["category_type"]
            category = {}
            category["trending_type"] = self.trending_types[t]
            if t == 1:
                cat["music_info"]["extra"] = json.loads(cat["music_info"]["extra"]) # this returns string for some reason
                beats = cat["music_info"]["extra"]["beats"]
                category["video_count"] = cat["music_info"]["user_count"]
                category["music"] = {
                    "artists": cat["music_info"]["artists"], # Most likely None
                    "music_id": cat["music_info"]["id_str"],
                    "music_length": cat["music_info"]["duration"],
                    "author": cat["music_info"]["author"],
                    "title": cat["music_info"]["title"],
                    "play_url": cat["music_info"]["play_url"]["uri"],
                    "music_id": cat["music_info"]["mid"],
                    "cover": cat["music_info"]["cover_large"]["url_list"][0]
                }
                if len(beats) != 0:
                    category["music"]["beats"] = beats # no idea what the fuck this is, probably frames or something
            elif t == 0:
                category["video_count"] = cat["challenge_info"]["user_count"]
                category["hashtag"] = {
                    'id': cat["challenge_info"]["cid"],
                    "name": cat["challenge_info"]["cha_name"],
                    "desc": cat["challenge_info"]["desc"],
                    "total_views": cat["challenge_info"]["view_count"]
                }
            category["videos"] = []
            for video in cat["aweme_list"]:
                category["videos"].append(self.format_cat_video(video))
            data.append(category)
        return data
            
    def format_cat_video(self, data):
        cat_data = {}
        cat_data["video_id"] = data["aweme_id"]
        cat_data["created_at_timestamp"] = data["create_time"]
        cat_data["created_at"] = str(datetime.fromtimestamp(data["create_time"]))
        cat_data["cover"] = data["video"]["cover"]["url_list"][0]
        return cat_data