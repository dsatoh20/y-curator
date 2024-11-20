from django.db import models
# from django.contrib.auth.models import User
from accounts.models import Account
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.validators import MinLengthValidator
from books.bookinfo import get_book_info
import string
import secrets

# Create your models here.
class BookRecord(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE,\
        related_name='message_owner')
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    isbn = models.TextField(max_length=100, blank=True, null=True)
    img_path = models.TextField(max_length=300, blank=True, null=True)
    title = models.TextField(max_length=100)
    first_author =models.TextField(max_length=100, blank=True, null=True)
    pub_year = models.IntegerField(default=0)
    genre = models.TextField(max_length=100)
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    summary = models.TextField(max_length=1000, blank=True, null=True)
    report = models.TextField(max_length=5000)
    good_count = models.IntegerField(default=0)
    chat_count = models.IntegerField(default=0)
    pub_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    edit_count = models.IntegerField(default=0)
    
    def __str__(self):
        return str(self.title) + '/' + str(self.first_author)
    def rm_hyphen(self):
        isbn = self.isbn
        if len(isbn) == 10:
            isbn = "978" + isbn
        isbn_hyphenless = isbn.replace('-', '')
        isbn_hyphenless = isbn_hyphenless.replace(' ', '')
        isbn_hyphenless = isbn_hyphenless.replace('\n', '')
        self.isbn = "https://ndlsearch.ndl.go.jp/thumbnail/{}.jpg".format(isbn_hyphenless)
        return str(self.isbn) + "入力されたISBNから、ハイフンを削除しました"
    def auto_fill(self):
        info = get_book_info(self.title, self.first_author)
        items = {"first_author": self.first_author, "img_path":self.img_path, "pub_year":self.pub_year, "summary":self.summary} # genreはGoogleBooksのcategories項目が分からなかったので、ひとまず手動入力で
        for label, item in items.items():
            if item == None or item == "":
                items[label] = info[label]
        # if items["genre"] == "-":
            # items["genre"] = info["genre"]
        self.first_author, self.img_path, self.pub_year, self.summary = items["first_author"], items["img_path"], int(items["pub_year"]), items["summary"]
    class Meta:
        ordering = ('-pub_date',)

class Companion(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='companion_owner')
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.user) + '(' + str(self.owner) + '\'s companion)'
        
class Group(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, \
        related_name='group_owner')
    title = models.CharField(max_length=100)
    member = models.ManyToManyField(Companion, related_name='member')
    invitation_code = models.CharField(max_length=100, validators=[MinLengthValidator(8)], default='l7DLuEgV6Edodfs7')
    
    def generate_invitation_code(self):
        alphabet = string.ascii_letters + string.digits
        invitation_code = ''.join(secrets.choice(alphabet) for i in range(16))
        invitation_code = self.title + invitation_code
        self.invitation_code = invitation_code
        print(invitation_code)
    
    def __str__(self):
        return '<' + self.title + '(' + str(self.owner) + ')>'
    
class Friend(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, \
        related_name='friend_owner')
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.user) + '(group:"' + str(self.group) + '")'
    
class Good(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, \
        related_name='good_owner')
    bookrecord = models.ForeignKey(BookRecord, on_delete=models.CASCADE)
    
    def __str__(self):
        return 'good for "' + str(self.bookrecord) + '" (by ' + \
            str(self.owner) + ')'

class Chat(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='chat_owner')
    app = "books"
    record = models.ForeignKey(BookRecord, on_delete=models.CASCADE)
    comment = models.TextField(max_length=500)
    pub_date = models.DateTimeField(auto_now_add=True)
    reply_id = models.IntegerField(default=-1)
    reply_count = models.IntegerField(default=0)
    def __str__(self):
        return "chat about " + str(self.record) 
    class Meta:
        ordering = ('pub_date',)

# class NewsRecord(models.Model):
# class CinemaRecord(models.Model):
# class PaperRecord(models.Model):
# class RakugoRecord(models.Model):
# class MusicRecord(models.Model):from django.db import models

# Create your models here.
