import requests
import json
from pprint import pprint

api = 'https://www.googleapis.com/books/v1/volumes?q=intitle:'
"""
url = api + "星の子"
res = requests.get(url).json()
n = res['totalItems']
item = res['items'][0]['volumeInfo']
pprint(item)
title = item['title']
first_author = item['authors'][0]
pub_date = item['publishedDate']
pub_year = pub_date.split("-")[0]
genre = item['categories'][0]
img_path = item['imageLinks']['thumbnail']
summary = item['description']
print(n)
print({"title": title, "first_author": first_author, "pub_year": pub_year, "genre": genre, "img_path": img_path, "summary": summary})
"""
def get_book_info(title, author=""):
    url = api + str(title)
    if author != "":
        url += "+inauthor:"
        url += author
    res = requests.get(url).json()
    n = res['totalItems']
    item = res['items'][0]['volumeInfo']
    pprint(item)
    title = item['title']
    try:
        first_author = item['authors'][0]
    except:
        first_author = ""
    pub_date = item['publishedDate']
    pub_year = pub_date.split("-")[0]
    try:
        genre = item['categories'][0]
    except:
        genre = "Others"
    try:
        img_path = item['imageLinks']['thumbnail']
    except:
        img_path = "/media/homepage_pics/logo.jpg"
    try:
        summary = item['description']
    except:
        summary = ""
    print({"title": title, "first_author": first_author, "pub_year": pub_year, "genre": genre, "img_path": img_path, "summary": summary})
    return {"title": title, "first_author": first_author, "pub_year": pub_year, "genre": genre, "img_path": img_path, "summary": summary}

# print(get_book_info('社会学'))