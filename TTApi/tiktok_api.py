import requests
import re
import json
import string
import random

from .music import Music
from .debug import Debug
from .video import Video
from .feed import Feed
from .comment import Comment
from .user import User


class TikTokApi:
    def __init__(self, headers={}, proxies={}, debug=False, **kwargs):
        """TikTokApi main class
        Args:
            headers (dict, optional): _description_. Defaults to {}.
            proxies (dict, optional): _description_. Defaults to {}.
            debug (bool, optional): _description_. Defaults to False.
            msToken (str, optional): _Required to get data from some endpoints, these usually expire after 24H_.
        """
        self.headers = {
            "user-agent": "okhttp/3.10.0.1"
        }
        if kwargs.get("session"):
            self.headers["cookie"] = "sessionid="+kwargs.get("session")
        self.region = kwargs.get("region") if kwargs.get("region") else "US"
        self.setup_headers(headers)
        self.params = {}
        self.setup_params(kwargs)
        self.session = requests.Session()
        self.session.proxies.update(proxies)
        self.session.headers.update(self.headers)
        
        """
            Methods
        """

        self.debug = Debug(debug)
        self.video = Video(self)
        self.feed = Feed(self)
        self.music = Music(self)
        self.comment = Comment(self)
        self.user = User(self)
        
        
    def setup_headers(self, headers) -> None:
        for key in headers:
            self.headers[key] = headers[key]
            
    def check_status_code(self, status) -> bool:
        if status > 206:
            return False
        else:
            return True
    
    def setup_params(self, args):
        if args.get("msToken"):
            self.params["msToken"] = args.get("msToken")
        if args.get("web_user_agent"):
            self.params["web_user_agent"] = args.get("web_user_agent")

    def parse_params(self, url) -> dict:
        param_dict = {}
        params = url.split("?")[1].split("&")
        for param in params:
            key = param.split("=")[0]
            value = param.split("=")[1]
            param_dict[key] = value
        return param_dict
    
    def write_json_to_file(self, j, filename):
        with open(filename, "w+") as f:
            f.write(json.dumps(j))
            f.close()