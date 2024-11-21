from linebots.bot_base import LineBotMSG
from linebots.bot_messages import create_message
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password

from accounts.models import Account

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import json, os
from cryptography.fernet import Fernet

LINE_SECRET_KEY = os.environ.get("LINE_SECRET_KEY")
if not LINE_SECRET_KEY:
    with open('linebots/conf.json', 'r') as f:
        data = json.load(f)
        LINE_SECRET_KEY = data["LINE_SECRET_KEY"]
fernet = Fernet(LINE_SECRET_KEY)

homepage_link = "https://ycurator.net"
comment_box_link = "https://docs.google.com/forms/d/e/1FAIpQLSffl6bNS5E_pVM_YToC1gJQkFDNA_494JuR3JOmLG87FI1axQ/viewform?usp=sf_link"


class LineBotApiView(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request, format=None):
        res = request.data
        response_text = {"text": "正常に検索されました。"} #レスポンスとして返す
        code = status.HTTP_200_OK #レスポンスのステータスコード
        if len(res['events']) > 0:
            data = res['events'][0] #リストの中に辞書がひとつ
            print(data)
            if data['type'] == 'message': # messageを受信したら
                print("メッセージ受信")
                message_obj = data['message']
                text = message_obj.get('text')
                user_info = data['source']
                userid = user_info['userId']
                user = Account.objects.filter(secret_key=str(text)).first()
                if text == "Y": # Yと入力されたら
                    msg = create_message("Yに表示されたSecretKeyを入力してください。\n（SecretKeyの認証に成功した場合、登録完了メッセージが表示されます。）") # SecretKey入力を誘導
                elif user != None: # 有効なSecretKeyが入力されたら
                    print("LINE連携準備")
                    if user.LINE_ID == "" or user.LINE_ID == None:
                        encrypted_useid = fernet.encrypt(bytes(userid, 'utf-8'))
                        user.LINE_ID = encrypted_useid # LINE_IDをアカウントに登録
                        user.save()
                        msg = create_message("LINEアカウントの登録が完了しました!\
                                以下リンクからYにログインしてください。\n" + str(homepage_link))
                    else: # LINE_IDがすでに登録されている場合
                        msg = create_message("このLINEアカウントは既にYのアカウントと紐づいています。")
                else:
                    reply_token = data['replyToken']
                    msg = create_message("メッセージありがとうございます。\nご意見ご要望は以下リンクからお願いいたします。\
                        \n"+str(comment_box_link))
                reply_token = data['replyToken']
                line_message = LineBotMSG(msg)
                line_message.reply(reply_token)
            elif data['type'] == 'follow': # followされた
                print("友達追加")
                user_info = data['source']
                userid = user_info['userId']
                # AccountのLINE_idを登録 --> Yの入力に誘導
                msg = create_message("友達追加ありがとうございます。\
                        以下リンクからYにログインしてください。\
                        \n" + str(homepage_link) +\
                            "\n フレンドの新規投稿のLINE通知を希望する場合、Yと入力してください。")
                line_message = LineBotMSG(msg)
                line_message.push(userid)
            elif data['type'] == 'unfollow':
                print("ブロック")
                user_info = data['source']
                userid = user_info['userId']
                # AccountのLINE_idを削除
                
                msg = create_message("友達解除残念です。")
            else:
                msg = create_message("なに？")
                userid = user_info['userId']
                line_message = LineBotMSG(msg)
                line_message.push(userid)
                
        else:
            response_text["text"] = "Webhookの確認" #確認時に返すレスポンス
        return Response(response_text, status=code)
        
