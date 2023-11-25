from datetime import datetime
import re

class Video:
    def __init__(self, api):
        self.api = api
        
    def download_video(self, video_url, watermark=False, filename=None, path=None):
        try:
            if 'is_play_url' in video_url:
                video_binary = self.get_video_binary(video_url)
                video_data = {'video_id': video_url.split("video_id=")[1].split("&")[0]}
            else:
                video_data = self.parse_video_data(video_url)
                video_binary = self.get_video_binary(video_data["download_urls"]["no_watermark" if not watermark else "watermark"])
            if not filename:
                filename = str(video_data["video_id"])+".mp4"
            if not path:
                path = filename
            with open(path, "wb") as v:
                v.write(video_binary)
                v.close()
            self.api.debug.success(f"Successfully downloaded video by @{video_data['username'] if 'username' in video_data else 'Unknown User'} (path: {path})")
            return video_data
        except Exception as e:
            self.api.debug.error(f"Failed to download video from url {video_url}: "+str(e))
            return False
        
    def get_video_binary(self, download_url):
        """
        DOWNLOAD_URL (str):
            Get this from the object that the parse_video_data function returns, it can either be download_video_url or download_video_url_watermark
            
        Returns:
            binary: Raw binary mp4 data        
        """
        try:
            video = self.api.session.get(download_url)
            binary = video.content
            self.api.debug.success(f"Received binary data ({video.elapsed.total_seconds()}s)")
            return binary
        except Exception as e:
            self.api.debug.error("Failed to download url "+download_url + ": "+e)
            
    def parse_video_data(self, url, raw=False) -> dict:
        """Grabs the video data from a tiktok video url
        
        URL/VIDEO_ID (str):
            https://vm.tiktok.com/ZMNnX3Q4q 
            7116227445648395526 
            https://www.tiktok.com/@peachyfitness4/video/7116227445648395526
        
        RAW (bool):
            Optional if u want the raw data tiktok provided from the video (this contains way more info)
            
        Returns:
            formatted data from the video in a json object 
            
        """
        video_id = ""
        mobile_share_regex = "(http(s)?:\/\/(vm\.)tiktok.com\/[a-zA-Z0-9\/]+|http(s)?:\/\/(www\.)tiktok.com\/t\/[a-zA-Z0-9\/]+\/)"
        website_share_regex = "http(s)?:\/\/(www\.)?tiktok.com\/@[A-Za-z0-9._]+\/video\/[0-9]+"
        is_mobile_url = re.search(mobile_share_regex, url)
        if is_mobile_url:
            url = self.api.session.get(url, allow_redirects=True).url
        is_website_url = re.search(website_share_regex, url)
        is_video_id = re.match("[0-9]+", url)
        if is_website_url:
            video_id = re.search("[0-9]+", url.split("/video/")[1])[0]
        if is_video_id:
            video_id = url
        if not is_website_url and not is_video_id:
            return False
        try:
            print(video_id)
            video_request = self.api.session.get(f"https://api2-19-h2.musical.ly/aweme/v1/aweme/detail/?aweme_id={video_id}&device_type=SM-G973N&region=US&media_type=4")
            print(video_request.status_code)
            print(video_request.json())
            video_data = video_request.json()["aweme_detail"]
            self.api.debug.success(f"Found video data for video_id {video_id}")
            if raw:
                data = video_data
            else:
                data = self.video_data_formatter(video_data)
        except Exception as e:
            self.api.debug.error(f"Could not find video data for video_id {video_id}: "+str(e))
            return False
        return data
    
    def video_data_formatter(self, video_data):
        data = {"download_urls": {}, "author": {}, "stats": {}, "music": {}}
        data["created_at_timestamp"] = video_data["create_time"]
        data["created_at"] = str(datetime.fromtimestamp(video_data["create_time"]))
        data["video_url"] = f'https://tiktok.com/@{video_data["author"]["unique_id"]}/video/{video_data["aweme_id"]}'
        data["video_id"] = video_data["aweme_id"]
        data["download_urls"]["no_watermark"] = self.highest_soundquality_download_url(video_data["video"])
        data["download_urls"]["watermark"] = video_data["video"]["download_addr"]["url_list"][2]
        data["author"]["avatar_url"] = video_data["author"]["avatar_larger"]["url_list"][0].replace("webp", "jpeg")
        data["author"]["username"] = video_data["author"]["unique_id"]
        data["author"]["nickname"] = video_data["author"]["nickname"]
        data["author"]["sec_uid"] = video_data["author"]["sec_uid"]
        data["author"]["user_id"] = video_data["author"]["uid"]
        data["description"] = video_data["desc"]
        data["video_length"] = video_data["video"]["duration"]/1000
        data["stats"] = {
            "comment_count": video_data["statistics"]["comment_count"],
            "likes": video_data["statistics"]["digg_count"],
            "downloads": video_data["statistics"]["download_count"],
            "views": video_data["statistics"]["play_count"],
            "shares": video_data["statistics"]["share_count"],
        }
        data["music"] = {
            "music_id": video_data["music"]["mid"],
            "album": video_data["music"]["album"],
            "title": video_data["music"]["title"],
            "author": video_data["music"]["author"],
            "length": video_data["music"]["duration"] 
        }
        return data
    
    def highest_soundquality_download_url(self, data):
        bit_rates = data["bit_rate"]
        bit_rates.sort(key=lambda key: key["bit_rate"], reverse=True)
        return bit_rates[0]["play_addr"]["url_list"][2]