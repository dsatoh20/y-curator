from django.urls import path
from linebots.views import LineBotApiView
urlpatterns = [
    #...
    path("webhook", LineBotApiView.as_view(), name="linebot-webhook"),
]