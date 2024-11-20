import urllib.request
import json, requests, os

try:
    with open('linebots/conf.json', 'r') as f:
        data = json.load(f)

    CHANNEL_ACCESS_TOKEN = data["CHANNEL_ACCESS_TOKEN"]
    CHANNEL_SECRET = data["CHANNEL_SECRET"]
except:
    CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
    CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")
"""
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

def main():
    to = ["送信対象のユーザIDをリスト型で指定"]
    messages = TextSendMessage(text="マルチキャストテスト")
    line_bot_api.multicast(to, messages=messages)

if __name__ == "__main__":
    main()
    
userid = requests.get()
"""


REPLY_ENDPOINT_URL = "https://api.line.me/v2/bot/message/reply"
PUSH_ENDPOINT_URL = "https://api.line.me/v2/bot/message/push"
MULTICAST_ENDPOINT_URL = "https://api.line.me/v2/bot/message/multicast"

ACCESSTOKEN = CHANNEL_ACCESS_TOKEN
HEADER = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + ACCESSTOKEN
}

class LineBotMSG():
    def __init__(self, messages):
        self.messages = messages

    def reply(self, reply_token):
        body = {
            'replyToken': reply_token,
            'messages': self.messages
        }
        
        req = urllib.request.Request(REPLY_ENDPOINT_URL, json.dumps(body).encode(), HEADER)
        
        try:
            with urllib.request.urlopen(req) as res:
                body = res.read()
        except urllib.error.HTTPError as err:
            print(err)
        except urllib.error.URLError as err:
            print(err.reason)
    def push(self, userid):
        body = {
            'to': userid,
            'messages': self.messages
        }
        req = urllib.request.Request(PUSH_ENDPOINT_URL, json.dumps(body).encode(), HEADER)
        try:
            with urllib.request.urlopen(req) as res:
                body = res.read()
        except urllib.error.HTTPError as err:
            print(err)
        except urllib.error.URLError as err:
            print(err.reason)
    def multicast(self, user_list):
        body = {
            'to': user_list,
            'messages': self.messages
        }
        req = urllib.request.Request(MULTICAST_ENDPOINT_URL, json.dumps(body).encode(), HEADER)
        try:
            with urllib.request.urlopen(req) as res:
                body = res.read()
        except urllib.error.HTTPError as err:
            print(err)
        except urllib.error.URLError as err:
            print(err.reason)