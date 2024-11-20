from django import forms
from django.contrib.auth.models import User
from .models import Account
from django.core.exceptions import ValidationError
from books.models import BookRecord, Group, Companion
from papers.models import PaperRecord
from movies.models import MovieRecord
from articles.models import ArticleRecord
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.files.images import get_image_dimensions

# アップロード画像のバリデーター
def validate_image(fieldfile_obj):
    filesize = fieldfile_obj.file.size
    megabyte_limit = 1
    if filesize > megabyte_limit*1024*1024:
        raise ValidationError("Image file too large ( > %s MB )" % str(megabyte_limit))
    if fieldfile_obj.content_type not in ['image/jpeg', 'image/png']:
        raise ValidationError("Image file type not supported")

# フォームクラス作成
class AccountForm(forms.ModelForm):
    # パスワード入力：非表示対応
    password = forms.CharField(widget=forms.PasswordInput(),label="PASSWORD")

    class Meta():
        # ユーザー認証
        model = User
        # フィールド指定
        fields = ('username','password')
        # フィールド名指定
        labels = {'username':"User ID"}
           
class AddAccountForm(forms.ModelForm):
    class Meta():
        # モデルクラスを指定
        model = Account
        fields = ('email','last_name','first_name','LINE_bool','account_image',)
        labels = {'email':'Email','last_name':"Last name",'first_name':"First name","LINE_bool":"LINE check",'account_image':"Profile photo",}
    def clean_account_image(self):
        img = self.cleaned_data['account_image']
        if img:
            megabyte_limit = 5
            filesize = img.size
            if filesize> megabyte_limit*1024*1024:
                raise ValidationError("Image file too large ( > %s MB )" % str(megabyte_limit))
            if img.content_type not in ['image/jpeg', 'image/png']:
                raise ValidationError("Image file type not supported")
        return img
class LINECheckForm(forms.Form):
    check = forms.BooleanField(
            label='Checkbox',
            required=False,
        )
class GroupCheckForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(GroupCheckForm, self).__init__(*args, **kwargs)
        public = Account.objects.filter(user__username='public').first()
        companions = Companion.objects.filter(user=user)
        self.fields['groups'] = forms.MultipleChoiceField(
            choices=[(item.title, item.title) for item in \
                Group.objects.filter(Q(owner__in=[user, public])|Q(member__in=companions)).distinct()],
            widget=forms.CheckboxSelectMultiple(),
            initial=[]
        )  

apps = ["Articles", "Books", "Movies", "Papers"]
class AppCheckForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AppCheckForm, self).__init__(*args, **kwargs)
        self.fields['apps'] = forms.MultipleChoiceField(
            choices=[(app, app) for app in apps],
            widget=forms.CheckboxSelectMultiple(),
            initial=[]
        )