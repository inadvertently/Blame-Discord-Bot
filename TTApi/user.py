from re import U
from .exceptions import msToken, web_user_agent
from .encryption.tiktok import *
import urllib.parse
class User:
    def __init__(self, api):
        self.api = api
        
        """
        Updating this later
        """