from django.db import models

# Create your models here.
from django.db import models
# ユーザー認証
from django.contrib.auth.models import User

from PIL import Image
import io
import string
import secrets
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator

# アップロード画像のバリデーター (機能していないがmigrationの関係で残している)
def validate_image(fieldfile_obj):
    filesize = fieldfile_obj.file.size
    megabyte_limit = 1
    if filesize > megabyte_limit*1024*1024:
        raise ValidationError("Image file too large ( > %s MB )" % str(megabyte_limit))
    if fieldfile_obj.file.content_type not in ['image/jpeg', 'image/png']:
        raise ValidationError("Image file type not supported")

# ユーザーアカウントのモデルクラス
class Account(models.Model):

    # ユーザー認証のインスタンス(1vs1関係)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # 追加フィールド
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    email = models.EmailField()
    account_image = models.ImageField(upload_to="profile_pics", blank=True)
    icon_image = models.ImageField(upload_to="profile_pics", blank=True, default="/profile_pics/default.jpg")
    
    # LINE通知用
    LINE_bool = models.BooleanField(default=False)
    secret_key = models.CharField(max_length=100, unique=True, validators=[MinLengthValidator(8)])
    LINE_ID = models.BinaryField(blank=True, null=True)
    
    # 閲覧履歴
    record_1 = models.CharField(blank=True, null=True, max_length=100, default="") # レコードの種類
    owner_1 = models.CharField(blank=True, null=True, max_length=100, default="") # レコードのid
    record_2 = models.CharField(blank=True, null=True, max_length=100, default="")
    owner_2 = models.CharField(blank=True, null=True, max_length=100, default="")
    record_3 = models.CharField(blank=True, null=True, max_length=100, default="")
    owner_3 = models.CharField(blank=True, null=True, max_length=100, default="")
    record_4 = models.CharField(blank=True, null=True, max_length=100, default="")
    owner_4 = models.CharField(blank=True, null=True, max_length=100, default="")
    record_5 = models.CharField(blank=True, null=True, max_length=100, default="")
    owner_5 = models.CharField(blank=True, null=True, max_length=100, default="")
    record_6 = models.CharField(blank=True, null=True, max_length=100, default="")
    owner_6 = models.CharField(blank=True, null=True, max_length=100, default="")
    record_7 = models.CharField(blank=True, null=True, max_length=100, default="")
    owner_7 = models.CharField(blank=True, null=True, max_length=100, default="")
    record_8 = models.CharField(blank=True, null=True, max_length=100, default="")
    owner_8 = models.CharField(blank=True, null=True, max_length=100, default="")
    
    # 閲覧履歴の更新
    def get_history(self, record, app="Books"):
        latest = [app, str(record.id)] # [種類, レコードID]
        spc = [self.record_1, self.record_2, self.record_3, self.record_4, self.record_5, self.record_6, self.record_7, self.record_8]
        ids = [self.owner_1, self.owner_2, self.owner_3, self.owner_4, self.owner_5, self.owner_6, self.owner_7, self.owner_8]
        records = []
        for i in range(len(spc)):
            records.append([spc[i], ids[i]])
        print("befor: ")
        print(ids)
        print(spc)
        if [app, str(record.id)] not in records:
            print(records)
            print([app, str(record.id)])
            spc.insert(0, app)
            del spc[-1]
            ids.insert(0, str(record.id))
            del ids[-1]
            self.record_1, self.record_2, self.record_3, self.record_4, self.record_5, self.record_6, self.record_7, self.record_8 = spc
            self.owner_1, self.owner_2, self.owner_3, self.owner_4, self.owner_5, self.owner_6, self.owner_7, self.owner_8 = ids
            print("not", ids)
            print("not", spc)
        else:
            index = records.index(latest)
            print("インデックス", index)
            del spc[index]
            spc.insert(0, app)
            del ids[index]
            ids.insert(0, str(record.id))
            self.record_1, self.record_2, self.record_3, self.record_4, self.record_5, self.record_6, self.record_7, self.record_8 = spc
            self.owner_1, self.owner_2, self.owner_3, self.owner_4, self.owner_5, self.owner_6, self.owner_7, self.owner_8 = ids
            print("yes", ids)
            print("yes", spc)
    # アップロード画像のバリデーター
    def img_validation(self):
        filesize = self.account_image.file.size
        megabyte_limit = 10.0
        msg = None
        if filesize > megabyte_limit*1024*1024:
            msg = "Image file too large ( > %s MB )" % str(megabyte_limit)
        if self.account_image.file.content_type not in ['image/jpeg', 'image/png']:
            msg = "Image file type not supported"
        return msg
        
    def transform(self):
        # 画像にマージンを追加し、64x64にリサイズして保存しなおす

        # 画像ファイル名を取得
        name = self.account_image.name
        # アップロードされたファイルから画像オブジェクト生成
        org_img = Image.open(self.account_image)

        # PILでの画像処理
        square_img = expand2square(org_img)
        ret_img = square_img.resize((64, 64))

        # 画像処理後の画像のデータをbufferに保存
        buffer = io.BytesIO()
        ret_img.save(fp=buffer, format=org_img.format)


        # 以前保存した画像ファイルを削除
        self.account_image.file.close()
        self.account_image.delete()
        try:
            self.icon_image.file.close()
            self.icon_image.delete()
        except:
            pass
        # bufferのデータをファイルとして保存（レコードの更新も行われる）
        self.icon_image.save(name=self.user.username+"_"+name, content=buffer)
        print(self.icon_image)
    
    def generate_secret_key(self):
        alphabet = string.ascii_letters + string.digits
        secret_key = ''.join(secrets.choice(alphabet) for i in range(8))
        secret_key = self.user.username + secret_key
        self.secret_key = secret_key
        print(secret_key)

    def __str__(self):
        return self.user.username
    
    
# 画像処理のための関数
def expand2square(pil_img, background_color=0):
    # マージンを追加して正方形にする
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result