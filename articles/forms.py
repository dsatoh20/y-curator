from django import forms
from books.models import BookRecord, Group, Friend, Good, Chat, Companion
from .models import ArticleRecord, ArticleChat
from accounts.models import Account
from django.db.models import Q

all_article_genres = [
    ('社会', '社会'),
    ('政治', '政治'),
    ('経済', '経済'),
    ('スポーツ', 'スポーツ'),
    ('国際', '国際'),
    ('地域', '地域'),
    ('科学・IT', '科学・IT'),
    ('エンタメ・文化', 'エンタメ・文化'),
    ('ライフ', 'ライフ'),
    ('教育・就活', '教育・就活'),
    ('医療・健康', '医療・健康'),
    ('--TEST-----', '--TEST-----'),
] # https://www.yomiuri.co.jp/category/news/

class ArticleRecordForm(forms.ModelForm):
    class Meta:
        model = ArticleRecord
        fields = ['first_author', 'pub_year', 'score', 'summary', 'report']
        widgets = {
            "first_author": forms.Textarea(attrs={'class': 'form-author form-common',
                                     'rows':1,
                                     'placeholder': "著者名"}),
            "pub_year": forms.DateInput(attrs={'class': 'form-year form-common',
                                     'rows':1,
                                     'placeholder': "投稿日"}),
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
        

class PostArticleForm(forms.Form):
    link = forms.CharField(required=False,
                           widget=forms.Textarea(attrs={'class': 'form-ISBN form-common',
                                                        'rows': 1,
                                                        'placeholder': "https://www.yomiuri.co.jp/politics/20240421-OYT1T50001/"}))
    title = forms.CharField(max_length=100, \
        widget=forms.Textarea(attrs={'class': 'form-title form-common',
                                     'rows': 1,
                                     'placeholder': "岸田総理の一日（20日）"}))
    first_author = forms.CharField(max_length=100, \
        widget=forms.Textarea(attrs={'class': 'form-author form-common',
                                     'rows':1,
                                     'placeholder': "読売新聞"}))
    pub_year = forms.DateField(\
        widget=forms.DateInput(attrs={'class': 'form-year form-common',
                                     'rows':1,
                                     'placeholder': "2024-04-21"}))
    genre = forms.ChoiceField(label='Genre', 
                              choices=[('-', '-')] + all_article_genres, 
                              widget=forms.Select(attrs={'class':'form-genre form-common'}))
    score = forms.IntegerField(max_value=10, min_value=1, initial=5,\
        widget=forms.NumberInput(attrs={'class': 'form-score form-common',
                                     'rows':1,
                                     'placeholder': "1~10の10段階評価"}))
    summary = forms.CharField(max_length=1000, \
        widget=forms.Textarea(attrs={'class': 'form-summary form-common',
                                     'rows':4,
                                     'placeholder': "1000字以内で入力してください。"}))
    report = forms.CharField(max_length=5000, \
        widget=forms.Textarea(attrs={'class': 'form-content form-common',
                                     'rows':10,
                                     'placeholder': "5000字以内で入力してください。"}))
    
    
    def __init__(self, user, *args, **kwargs):
        super(PostArticleForm, self).__init__(*args, **kwargs)
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
                                                            'placeholder': 'コメントを50字以内で入力してください。'}))
class ReplyForm(forms.Form):
    comment = forms.CharField(max_length=500, min_length=1,
                               widget=forms.Textarea(attrs={'class':'form-comment',
                                                            'id': 'id_reply',
                                                            'rows':2,
                                                            'placeholder': '500字以内で入力してください。'}))

class ArticleGenreSelectForm(forms.Form):
    genre = forms.ChoiceField(
        choices=[('-', '-')] + [genre for genre in all_article_genres],
        widget=forms.Select(attrs={'class':'form-genre form-common'}),
    )
    def clean_genre(self):
        cleaned_data = super().clean()
        genre = cleaned_data['genre']
        if genre == '-' or genre == ('-', '-'):
            raise forms.ValidationError('ジャンルを選択してください。')
        return genre