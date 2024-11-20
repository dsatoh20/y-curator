from django.urls import path
from . import views
# from accounts import views as aviews
app_name = 'books'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:page>', views.index, name='index'),
    path('groups', views.groups, name='groups'),
    path('add', views.add, name='add'),
    path('creategroup', views.creategroup, name='creategroup'),
    path('post', views.post, name='post'),
    path('good/<int:good_id>', views.good, name='good'),
    path('chat/<int:chat_id>', views.chat, name='chat'),
    path('chat/<int:chat_id>/reply/<int:reply_id>', views.reply, name='reply'),
    path('edit/<int:edit_id>', views.edit, name='edit'),
    path('delete/<int:del_id>', views.delete, name='delete'),
    path('friend', views.friend, name='friend'),
    path('repost/<int:repost_id>', views.repost, name='repost'),
    path('highlight/<int:highlight_id>', views.highlight, name='highlight')
]
