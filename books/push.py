# レコードの新規投稿をLINEに通知
from linebot import LineBotApi
from linebot.models import TextSendMessage
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import urllib.request
import json
import requests

from linebots.bot_base import CHANNEL_ACCESS_TOKEN, MULTICAST_ENDPOINT_URL, ACCESSTOKEN, HEADER
from linebots.bot_messages import create_message

# リモートリポジトリに"ご自身のチャネルのアクセストークン"をpushするのは、避けてください。
# 理由は、そのアクセストークンがあれば、あなたになりすまして、プッシュ通知を送れてしまうからです。
LINE_CHANNEL_ACCESS_TOKEN = CHANNEL_ACCESS_TOKEN

headers = {
    "Content_Type": "application/json",
    "Authorization": "Bearer " + 'YOUR_CHANNEL_ACCESS_TOKEN'
    }

def SendMsg(user_list, messages):
    print("messagesは", messages)
    res = requests.post(MULTICAST_ENDPOINT_URL, 
                        headers=HEADER, 
                        json={
                            "to": user_list,
                            "messages": messages
                        }
                        )
    print(res.status_code)  # Prints the HTTP status code
    print(res.json())