from django.db import models
# from django.contrib.auth.models import User
from accounts.models import Account
from django.core.validators import MaxValueValidator, MinValueValidator

from books.models import Group, Companion

# Create your models here.
class ArticleRecord(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE,\
        related_name='article_owner')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    link = models.TextField(max_length=100, blank=True, null=True)
    title = models.TextField(max_length=100)
    first_author =models.TextField(max_length=100)
    pub_year = models.DateField()
    genre = models.TextField(max_length=100)
    genre_img = models.TextField(blank=True, null=True)
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    summary = models.TextField(max_length=1000)
    report = models.TextField(max_length=5000)
    good_count = models.IntegerField(default=0)
    chat_count = models.IntegerField(default=0)
    pub_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    edit_count = models.IntegerField(default=0)
    
    def __str__(self):
        return str(self.title) + '/' + str(self.first_author)
    def rm_space(self):
        link = self.link
        link_spaceless = link.replace(' ', '')
        link_spaceless = link_spaceless.replace('/n', '')
        self.link = link_spaceless
        return str(self.link) + "入力されたlinkから、spaceを削除しました"
    # genreに応じた画像を取得する
    def get_genre_img(self):
        genre_ref = {"社会": "society", "政治": "politics", "経済": "economy", \
            "スポーツ": "sports", "国際": "international", "地域": "community", \
                "科学・IT": "science", "エンタメ・文化": "entertainment","ライフ": "life", "教育・就活": "education",\
                    "医療・健康": "medical", "--TEST-----": "test"}
        self.genre_img = "/media/news_genres/" + str(genre_ref[self.genre]) + ".jpg"
        return self.genre_img
    class Meta:
        ordering = ('-pub_date',)

class ArticleChat(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='articlechat_owner')
    app = "articles"
    record = models.ForeignKey(ArticleRecord, on_delete=models.CASCADE)
    comment = models.TextField(max_length=500)
    pub_date = models.DateTimeField(auto_now_add=True)
    reply_id = models.IntegerField(default=-1)
    reply_count = models.IntegerField(default=0)
    def __str__(self):
        return "articlechat about " + str(self.record) 
    class Meta:
        ordering = ('pub_date',)