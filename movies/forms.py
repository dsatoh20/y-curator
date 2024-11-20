from django import forms
from books.models import BookRecord, Group, Friend, Good, Chat, Companion
from .models import MovieRecord, MovieChat
from accounts.models import Account
from django.db.models import Q

all_movie_genres = [
    ('Action', 'Action'),
    ('Adventure', 'Adventure'),
    ('Animation', 'Animation'),
    ('Comedy', 'Comedy'),
    ('Crime', 'Crime'),
    ('Documentary', 'Documentary'),
    ('Drama', 'Drama'),
    ('Family', 'Family'),
    ('Fantasy', 'Fantasy'),
    ('History', 'History'),
    ('Horror', 'Horror'),
    ('Music', 'Music'),
    ('Mystery', 'Mystery'),
    ('Romance', 'Romance'),
    ('Science Fiction', 'Science Fiction'),
    ('Thriller', 'Thriller'),
    ('TV Movie', 'TV Movie'),
    ('War', 'War'),
    ('Western', 'Western'),    
    ('--TEST----', '--TEST----'),
] # https://filmarks.com/list/genre

class MovieRecordForm(forms.ModelForm):
    class Meta:
        model = MovieRecord
        fields = ['director', 'pub_year', 'score', 'summary', 'report']
        widgets = {
            "director": forms.Textarea(attrs={'class': 'form-author form-common',
                                     'rows':1,
                                     'placeholder': "監督"}),
            "pub_year": forms.NumberInput(attrs={'class': 'form-year form-common',
                                     'rows':1,
                                     'placeholder': "公開年"}),
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
        

class PostMovieForm(forms.Form):
    title = forms.CharField(max_length=100, required=False,\
        widget=forms.Textarea(attrs={'class': 'form-title form-common',
                                     'rows': 1,
                                     'placeholder': "2001: A Space Odyssey"}))
    director = forms.CharField(max_length=100, required=False,\
        widget=forms.Textarea(attrs={'class': 'form-author form-common',
                                     'rows':1,
                                     'placeholder': "Stanley Kubrick"}))
    pub_year = forms.CharField(max_length=100, required=False,\
        widget=forms.NumberInput(attrs={'class': 'form-year form-common',
                                     'rows':1,
                                     'placeholder': "1968"}))
    genre = forms.ChoiceField(label='Genre', required=False,
                              choices=[('-', '-')] + all_movie_genres, 
                              widget=forms.Select(attrs={'class':'form-genre form-common'}))
    score = forms.IntegerField(max_value=10, min_value=1, initial=5,\
        widget=forms.NumberInput(attrs={'class': 'form-score form-common',
                                     'rows':1,
                                     'placeholder': "1~10の10段階評価"}))
    summary = forms.CharField(max_length=1000, required=False,\
        widget=forms.Textarea(attrs={'class': 'form-summary form-common',
                                     'rows':4,
                                     'placeholder': "1000字以内で入力してください。"}))
    report = forms.CharField(max_length=5000, \
        widget=forms.Textarea(attrs={'class': 'form-content form-common',
                                     'rows':10,
                                     'placeholder': "5000字以内で入力してください。"}))
    
    
    def __init__(self, user, *args, **kwargs):
        super(PostMovieForm, self).__init__(*args, **kwargs)
        companions = Companion.objects.filter(user=user)
        gps = Group.objects.filter(Q(owner=user)|Q(member__in=companions)|Q(title="public")).distinct() # 自分がownerのグループ or 自分がmemberに追加されているグループ
        self.fields['group'] = forms.ChoiceField(
            choices=[('-', '-')] + [(item.title, item.title)\
                for item in gps],
            widget=forms.Select(attrs={'class':'form-group form-common'}),
        )
    """
    def clean_genre(self):
        cleaned_data = super().clean()
        genre = cleaned_data['genre']
        if genre == '-' or genre == ('-', '-'):
            raise forms.ValidationError('ジャンルを選択してください。')
        return genre   
    """ 
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

class MovieGenreSelectForm(forms.Form):
    genre = forms.ChoiceField(
        choices=[('-', '-')] + [genre for genre in all_movie_genres],
        widget=forms.Select(attrs={'class':'form-genre form-common'}),
    )
    def clean_genre(self):
        cleaned_data = super().clean()
        genre = cleaned_data['genre']
        if genre == '-' or genre == ('-', '-'):
            raise forms.ValidationError('ジャンルを選択してください。')
        return genre   