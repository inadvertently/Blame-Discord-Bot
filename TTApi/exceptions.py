class No_Response(Exception):
    """Raised when tiktok doesn't return any response, there might not be a problem with you so try again. Sometimes tiktok does weird things."""
    def __init__(self, message="Tiktok returned no response, this might just be a check on their backend or some error. Try again."):
        self.message = message
        super().__init__(self.message)

class msToken(Exception):
    """Raised when u have not set msToken as an kwarg in the TikTokApi class"""
    def __init__(self, func, message="Could not find any msToken passed in the TikTokApi class kwargs"):
        message += f" ({func})"
        self.message = message
        super().__init__(self.message)

class web_user_agent(Exception):
    """Raised when u have not set web_user_agent and you are trying to use website endpoints"""
    def __init__(self, func, message="Could not find web_user_agent passed in the TikTokApi class kwargs, which is required when using "):
        message += func
        self.message = message
        super().__init__(self.message)