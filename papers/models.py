from django.db import models
# from django.contrib.auth.models import User
from accounts.models import Account
from django.core.validators import MaxValueValidator, MinValueValidator

from books.models import Group, Companion

# Create your models here.
class PaperRecord(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE,\
        related_name='paper_owner')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    doi = models.TextField(max_length=100, blank=True, null=True)
    title = models.TextField(max_length=100)
    first_author =models.TextField(max_length=100)
    pub_year = models.IntegerField(default=0)
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
        doi = self.doi
        doi_spaceless = doi.replace(' ', '')
        doi_spaceless = doi_spaceless.replace('/n', '')
        self.doi = doi_spaceless
        return str(self.doi) + "入力されたDOIから、spaceを削除しました"
    # genreに応じた画像を取得する
    def get_genre_img(self):
        genre_ref = {"文学": "literature", "法学": "law", "経済学": "economics", \
            "理学": "science", "工学": "engineering", "農学": "agriculture", \
                "医学": "medicine", "複合領域": "complex", "--TEST---": "test"}
        self.genre_img = "/media/academic_areas/" + str(genre_ref[self.genre]) + ".jpg"
        return self.genre_img
    class Meta:
        ordering = ('-pub_date',)

class PaperChat(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='paperchat_owner')
    app = "papers"
    record = models.ForeignKey(PaperRecord, on_delete=models.CASCADE)
    comment = models.TextField(max_length=500)
    pub_date = models.DateTimeField(auto_now_add=True)
    reply_id = models.IntegerField(default=-1)
    reply_count = models.IntegerField(default=0)
    def __str__(self):
        return "paperchat about " + str(self.record) 
    class Meta:
        ordering = ('pub_date',)