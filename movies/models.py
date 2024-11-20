from django.db import models
# from django.contrib.auth.models import User
from accounts.models import Account
from django.core.validators import MaxValueValidator, MinValueValidator

from books.models import Group, Companion
from movies.movinfo import get_movie_info

# Create your models here.
class MovieRecord(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE,\
        related_name='movie_owner')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    title = models.TextField(max_length=100)
    director =models.TextField(max_length=100, blank=True, null=True)
    img_path = models.TextField(max_length=100, blank=True, null=True)
    pub_year = models.IntegerField(default=0)
    genre = models.TextField(max_length=100, blank=True, null=True)
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    summary = models.TextField(max_length=1000, blank=True, null=True)
    report = models.TextField(max_length=5000)
    good_count = models.IntegerField(default=0)
    chat_count = models.IntegerField(default=0)
    pub_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    edit_count = models.IntegerField(default=0)
    
    def __str__(self):
        return str(self.title) + '/' + str(self.director)
    def auto_fill(self):
        info = get_movie_info(self.title)
        items = {"director": self.director, "img_path":self.img_path, "pub_year":self.pub_year, "genre":self.genre, "summary":self.summary}
        for label, item in items.items():
            if item == None or item == "":
                items[label] = info[label]
        self.director, self.img_path, self.pub_year, self.genre, self.summary = \
            items["director"], items["img_path"], int(items["pub_year"]), items["genre"], items["summary"]
    class Meta:
        ordering = ('-pub_date',)

class MovieChat(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='moviechat_owner')
    app = "movies"
    record = models.ForeignKey(MovieRecord, on_delete=models.CASCADE)
    comment = models.TextField(max_length=500)
    pub_date = models.DateTimeField(auto_now_add=True)
    reply_id = models.IntegerField(default=-1)
    reply_count = models.IntegerField(default=0)
    def __str__(self):
        return "moviechat about " + str(self.record) 
    class Meta:
        ordering = ('pub_date',)