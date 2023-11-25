from datetime import datetime


class Comment:
    def __init__(self, api):
        self.api = api
    
    def get_comments(self, video_id, cursor="0", count="20", region="US", raw=False):
        comments = self.api.session.get(f"https://api2-19-h2.musical.ly/aweme/v1/comment/list/?aweme_id={video_id}&cursor={cursor}&count={count}&comment_style=2&device_type=SM-G973N&region={region}")
        res = comments.json()
        return self.format_comments(res["comments"], raw)

    def get_replies(self, comment_id, count="20", cursor="0", raw=False):
        replies = self.api.session.get(f"https://api2-19-h2.musical.ly/aweme/v1/comment/list/reply/?comment_id={comment_id}&cursor={cursor}&count={count}&comment_style=2&device_type=SM-G973N&media_type=4")
        res = replies.json()
        return self.format_comments(res["comments"], raw=raw)

    def format_comments(self, comments_data, raw=False, replies=False):
        if raw:
            return comments_data
        comments = []
        for comment in comments_data:
            data = self.parse_comment_data(comment, replies)
            comments.append(data)
        return comments

    def parse_comment_data(self, comment, replies=False):
        data = {}
        commenter = comment["user"]
        data["comment_id"] = comment["cid"]
        data["likes"] = comment["digg_count"]
        data["text"] = comment["text"]
        data["created_at_timestamp"] = comment["create_time"]
        data["created_at"] = str(datetime.fromtimestamp(comment["create_time"]))
        if 'reply_comment_total' in comment:
            data["total_replies"] = comment["reply_comment_total"]
        data["replied_to_id"] = comment["reply_to_reply_id"]
        if replies:
            data["replies"] = self.get_replies(comment["cid"]) # might be empty might not be, if empty then request the replies by comment.get_replies
        data["commenter"] = {
            "nickname": commenter["nickname"],
            "user_id": commenter["uid"],
            "sec_uid": commenter["sec_uid"],
            "username": commenter["unique_id"],
            "avatar_url": commenter["avatar_larger"]["url_list"][2],
            "signature": commenter["signature"],
            "region": commenter["region"],
            "verified": commenter["is_star"] # pretty sure this is verified or not?
        }
        return data