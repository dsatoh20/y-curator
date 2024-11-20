from typing import Any
from django import forms
from.models import BookRecord, Group, Friend, Good, Chat, Companion
from accounts.models import Account
from django.db.models import Q

all_genres = [
    ('文学・評論', '文学・評論'),
    ('ノンフィクション', 'ノンフィクション'),
    ('ビジネス・経済', 'ビジネス・経済'),
    ('歴史・地理', '歴史・地理'),
    ('政治・社会', '政治・社会'),
    ('芸能・エンターテインメント', '芸能・エンターテインメント'),
    ('アート・建築・デザイン', 'アート・建築・デザイン'),
    ('人文・思想・宗教', '人文・思想・宗教'),
    ('暮らし・健康・料理', '暮らし・健康・料理'),
    ('サイエンス・テクノロジー', 'サイエンス・テクノロジー'),
    ('趣味・実用', '趣味・実用'),
    ('教育・自己啓発', '教育・自己啓発'),
    ('スポーツ・アウトドア', 'スポーツ・アウトドア'),
    ('事典・年鑑・本・ことば', '事典・年鑑・本・ことば'),
    ('音楽', '音楽'),
    ('旅行・紀行', '旅行・紀行'),
    ('絵本・児童書', '絵本・児童書'),
    ('コミックス', 'コミックス'),
    ('--TEST--', '--TEST--'),
]

class BookRecordForm(forms.ModelForm):
    class Meta:
        model = BookRecord
        fields = ['first_author', 'pub_year', 'score', 'summary', 'report']
        widgets = {
            "first_author": forms.Textarea(attrs={'class': 'form-author form-common',
                                     'rows':1,
                                     'placeholder': "著者名"}),
            "pub_year": forms.NumberInput(attrs={'class': 'form-year form-common',
                                     'rows':1,
                                     'placeholder': "出版年"}),
            "score": forms.NumberInput(attrs={'class': 'form-score form-common',
                                     'rows':1,
                                     'placeholder': "1~10の10段階評価"}),
            "summary": forms.Textarea(attrs={'class': 'form-summary form-common',
                                     'rows':4,
                                     'placeholder': "1000字以内で入力してください。"}),
            "report": forms.Textarea(attrs={'class': 'form-content form-common',
                                     'rows':4,
                                     'placeholder': "5000字以内で入力してください。"})
        }
        
        
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['owner', 'title']
        
class FriendForm(forms.ModelForm):
    class Meta:
        model = Friend
        fields = ['owner', 'user', 'group']
        
class GoodForm(forms.ModelForm):
    class Meta:
        model = Good
        fields = ['owner', 'bookrecord']

        
class GroupCheckForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(GroupCheckForm, self).__init__(*args, **kwargs)
        public = Account.objects.filter(user__username='public').first()
        companions = Companion.objects.filter(user=user)
        self.fields['groups'] = forms.ChoiceField(
            choices=[('-', '-')] + [(item.title, item.title) for item in \
                Group.objects.filter(Q(owner__in=[user, public])|Q(member__in=companions)).distinct()],
            widget=forms.Select(attrs={'class':'form-group form-common'}),
            required=False,
        )

class GroupSelectForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(GroupSelectForm, self).__init__(*args, **kwargs)
        companions = Companion.objects.filter(user=user)
        self.fields['groups'] = forms.ChoiceField(
            choices=[('-', '-')] + [(item.title, item.title) \
                for item in Group.objects.filter(Q(owner=user)|Q(member__in=companions)).distinct()],\
            widget=forms.Select(attrs={'class':'form-group form-common'}),
        )
    def clean_groups(self):
        groups = self.cleaned_data.get('groups')
        if groups == '-' or groups == ('-', '-'):
            raise forms.ValidationError('グループを選択してください。')
        return groups
        
class FriendsForm(forms.Form):
    def __init__(self, user, friends=[], vals=[], *args, **kwargs):
        super(FriendsForm, self).__init__(*args, **kwargs)
        self.fields['friends'] = forms.MultipleChoiceField(\
            choices=[(item.user, item.user) for item in friends], \
                widget=forms.CheckboxSelectMultiple(attrs={'class':'form-friend form-common'}), \
                    initial=vals,
        )
        
class CompanionsForm(forms.Form):
    def __init__(self, user, companions=[], vals=[], *args, **kwargs):
        super(CompanionsForm, self).__init__(*args, **kwargs)
        self.fields['friends'] = forms.MultipleChoiceField(\
            choices=[(item.user, item.user) for item in companions], \
                widget=forms.CheckboxSelectMultiple(), \
                    initial=vals,
        )
        
class FindUserForm(forms.Form):
    find = forms.EmailField(label='find', required=False, \
        widget=forms.TextInput(attrs={'class': 'form-common'}))

class CreateGroupForm(forms.Form):
    group_name = forms.CharField(max_length=10, \
        widget=forms.TextInput(attrs={'class': 'form-group'}))

class PostForm(forms.Form):
    # isbn = forms.CharField(required=False, max_length=20, min_length=10,
                           # widget=forms.Textarea(attrs={'class': 'form-ISBN form-common',
                                                        # 'rows': 1,
                                                        # 'placeholder': "978-4-04-604137-1"}))
    title = forms.CharField(max_length=100, \
        widget=forms.Textarea(attrs={'class': 'form-title form-common',
                                     'rows': 1,
                                     'placeholder': "俺か、俺以外か　ローランドという生き方"}))
    first_author = forms.CharField(max_length=100, required=False,\
        widget=forms.Textarea(attrs={'class': 'form-author form-common',
                                     'rows':1,
                                     'placeholder': "ROLAND"}))
    pub_year = forms.IntegerField(max_value=3000,  required=False,\
        widget=forms.Textarea(attrs={'class': 'form-year form-common',
                                     'rows':1,
                                     'placeholder': "2019"}))
    genre = forms.ChoiceField(label='Genre',
                              choices=[('-', '-')] + [genre for genre in all_genres],
                              widget=forms.Select(attrs={'class':'form-genre form-common'}))
    score = forms.IntegerField(max_value=10, min_value=1, initial=5,\
        widget=forms.NumberInput(attrs={'class': 'form-score form-common',
                                     'rows':1,
                                     'placeholder': "1~10の10段階評価"}))
    summary = forms.CharField(max_length=1000,  required=False,\
        widget=forms.Textarea(attrs={'class': 'form-summary form-common',
                                     'rows':4,
                                     'placeholder': "1000字以内で入力してください。"}))
    report = forms.CharField(max_length=5000, \
        widget=forms.Textarea(attrs={'class': 'form-content form-common',
                                     'rows':10,
                                     'placeholder': "5000字以内で入力してください。"}))
    
    
    def __init__(self, user, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        companions = Companion.objects.filter(user=user)
        gps = Group.objects.filter(Q(owner=user)|Q(member__in=companions)|Q(title="public")).distinct() # 自分がownerのグループ or 自分がmemberに追加されているグループ
        self.fields['group'] = forms.ChoiceField(
            choices=[('-', '-')] + [(item.title, item.title)\
                for item in gps],
            widget=forms.Select(attrs={'class':'form-group form-common'}),
        )
    
    def clean_genre(self):
        cleaned_data = super().clean()
        genre = cleaned_data['genre']
        if genre == '-' or genre == ('-', '-'):
            raise forms.ValidationError('ジャンルを選択してください。')
        return genre
    def clean_group(self):
        cleaned_data = super().clean()
        group = cleaned_data['group']
        if group == '-' or group == ('-', '-'):
            raise forms.ValidationError('グループを選択してください。')
        return group
        
class ChatForm(forms.Form):
    comment = forms.CharField(max_length=50, min_length=1,
                               widget=forms.Textarea(attrs={'class':'form-comment',
                                                            'rows':2,
                                                            'placeholder': '50字以内で入力してください。'}))
class ReplyForm(forms.Form):
    comment = forms.CharField(max_length=500, min_length=1,
                               widget=forms.Textarea(attrs={'class':'form-comment',
                                                            'id': 'id_reply',
                                                            'rows':2,
                                                            'placeholder': '500字以内で入力してください。'}))
              

class GenreSelectForm(forms.Form):
    genre = forms.ChoiceField(
        choices=[('-', '-')] + [genre for genre in all_genres],
        widget=forms.Select(attrs={'class':'form-genre form-common'}),
    )
    def clean_genre(self):
        cleaned_data = super().clean()
        genre = cleaned_data['genre']
        if genre == '-' or genre == ('-', '-'):
            raise forms.ValidationError('ジャンルを選択してください。')
        return genre   
