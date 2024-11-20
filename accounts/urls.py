from django.urls import path
from . import views
from books import views as bviews
from papers import views as pviews
from movies import views as mviews
from articles import views as aviews

urlpatterns = [
    path('',views.Login,name='Login'),
    path("logout",views.Logout,name="Logout"),
    path('register/',views.AccountRegistration.as_view(), name='SignUp'),
    path("home",views.home,name="home"),
    path('home<int:page>', views.home, name='home'),
    path('books',bviews.index,name='Books'),
    path('papers', pviews.index, name='Papers'),
    path('articles',aviews.index,name='Articles'),
    path('movies', mviews.index, name='Movies'),
    path('profile', views.Profile, name="profile"),
    path('contact',views.contact, name='contact'),
    path('link', views.link, name='link'),
    path("records/<int:user_id>", views.records, name="records"),
    path("records/<int:user_id>/<int:page>", views.records, name="records"),
    path("forum", views.forum, name="forum"),
]
