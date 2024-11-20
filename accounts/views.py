from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import TemplateView #テンプレートタグ
from .forms import AccountForm, AddAccountForm, LINECheckForm #ユーザーアカウントフォーム
from django.contrib import messages
import random
import datetime
from dateutil.relativedelta import relativedelta

# ログイン・ログアウト処理に利用
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Account

from PIL import Image
from books.models import BookRecord, Group, Companion, Chat
from papers.models import PaperRecord, PaperChat
from movies.models import MovieRecord, MovieChat
from articles.models import ArticleRecord, ArticleChat

from django.core.paginator import Paginator
from django.db.models import Q

from books.forms import all_genres
from papers.forms import all_paper_genres
from movies.forms import all_movie_genres
from articles.forms import all_article_genres

from .forms import GroupCheckForm, AppCheckForm
from books.views import line_notification

# グラフ描画用
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64


#ログイン
def Login(request):
    # POST
    if request.method == 'POST':
        # フォーム入力のユーザーID・パスワード取得
        ID = request.POST.get('userid')
        Pass = request.POST.get('password')

        # Djangoの認証機能
        user = authenticate(username=ID, password=Pass)

        # ユーザー認証
        if user:
            #ユーザーアクティベート判定
            if user.is_active:
                # ログイン
                login(request,user)
                # `next`パラメータの取得
                next_url = request.POST.get('next')
                # `next`パラメータがあればそこに、なければホームにリダイレクト
                return redirect(next_url) if next_url else redirect('home')
                # ホームページ遷移
                # return HttpResponseRedirect(reverse('home'))
            else:
                # アカウント利用不可
                return HttpResponse("Invalid account.")
        # ユーザー認証失敗
        else:
            messages.success(request, "Incorrect email or password.")
            # return HttpResponse("Incorrect email or password.")
            return redirect(to="/")
    # GET
    else:
        if request.user_agent.is_mobile:
            return render(request, 'accounts_mobile_HTML/login.html')
        else:
            return render(request, 'accounts_HTML/login.html')


#ログアウト
@login_required
def Logout(request):
    logout(request)
    # ログイン画面遷移
    messages.success(request, "Logged out.")
    return HttpResponseRedirect(reverse('Login'))


#ホーム
@login_required
def home(request, page=1):
    # ログイン中のユーザーを取得
    user = Account.objects.get(user=request.user)
    
    # POST
    if request.method == 'POST':
        # フォームの用意
        groupcheckform = GroupCheckForm(user, request.POST)
        appcheckform = AppCheckForm(request.POST)
        # groupタイトルの取得
        glist = []
        for item in request.POST.getlist('groups'):
            glist.append(item)
        # appの取得
        alist = []
        for item in request.POST.getlist('apps'):
            alist.append(item)
        records = get_proper_records(user, page, glist, alist)
    # GET
    else:
        # フォームの用意
        groupcheckform = GroupCheckForm(user)
        appcheckform = AppCheckForm()
        # レコードを取得
        records = get_records(user, page)
    # 共通
    recom = get_one_record(user)
    
    today = datetime.date.today()
    months = [today - relativedelta(months=i) for i in range(0, 7)]
    months.reverse()

    print("---------------------------", months)
    n_records = []
    n_comments = []
    for i in range(0, 7):
        n_record, n_comment = user_engagement(user, months[i])
        n_records.append(n_record)
        n_comments.append(n_comment)
    print(n_records, n_comments)
    create_graph(n_records, n_comments, months)
    graph = get_image()
    
    
    
    
    pgenre = [genre[0] for genre in all_paper_genres]
    bgenre = [genre[0] for genre in all_genres]
    mgenre = [genre[0] for genre in all_movie_genres]
    agenre = [genre[0] for genre in all_article_genres]
    # 閲覧履歴を取得
    hist_dict = [[user.record_1, user.owner_1], 
                 [user.record_2, user.owner_2], 
                 [user.record_3, user.owner_3], 
                 [user.record_4, user.owner_4], 
                 [user.record_5, user.owner_5], 
                 [user.record_6, user.owner_6], 
                 [user.record_7, user.owner_7], 
                 [user.record_8, user.owner_8]] # [app, id]のリスト
    hist_record_list = []
    for app, recid in hist_dict:
        if app == "Books":
            try:
                hist_record_list.append(BookRecord.objects.get(id=int(recid)))
            except:
                hist_record_list.append(BookRecord.objects.get(title="---dummy---"))
        elif app == "Papers":
            try:
                hist_record_list.append(PaperRecord.objects.get(id=int(recid)))
            except:
                hist_record_list.append(BookRecord.objects.get(title="---dummy---"))
        elif app == "Movies":
            try:
                hist_record_list.append(MovieRecord.objects.get(id=int(recid)))
            except:
                hist_record_list.append(BookRecord.objects.get(title="---dummy---"))
        elif app == "Articles":
            try:
                hist_record_list.append(ArticleRecord.objects.get(id=int(recid)))
            except:
                hist_record_list.append(BookRecord.objects.get(title="---dummy---"))
        elif app == "" or app == None:
            hist_record_list.append(BookRecord.objects.get(title="---dummy---"))
    params = {
        "login_user":user,
        "contents": records,
        "pgenre": pgenre,
        "bgenre": bgenre,
        "mgenre": mgenre,
        "agenre": agenre,
        "record1": hist_record_list[0],
        "record2": hist_record_list[1],
        "record3": hist_record_list[2],
        "record4": hist_record_list[3],
        "record5": hist_record_list[4],
        "record6": hist_record_list[5],
        "record7": hist_record_list[6],
        "record8": hist_record_list[7],
        "appform": appcheckform,
        "groupform": groupcheckform,
        "recom": recom,
        "graph": graph,
        }
    if request.user_agent.is_mobile:
            return render(request, 'accounts_mobile_HTML/home.html', params)
    else:
        return render(request, "accounts_HTML/home.html",context=params)
@login_required
def records(request, user_id, page=1):
    # ログイン中のユーザーを取得
    user = Account.objects.get(user=request.user)
    friend = Account.objects.get(id=user_id)
    # レコードを取得
    records = get_friend_records(user, page, friend)
    pgenre = [genre[0] for genre in all_paper_genres]
    bgenre = [genre[0] for genre in all_genres]
    mgenre = [genre[0] for genre in all_movie_genres]
    agenre = [genre[0] for genre in all_article_genres]
    params = {
        "login_user": user,
        "friend": friend,
        "contents": records,
        "pgenre": pgenre,
        "bgenre": bgenre,
        "mgenre": mgenre,
        "agenre": agenre,
        }
    if request.user_agent.is_mobile:
            return render(request, 'accounts_mobile_HTML/records.html', params)
    else:
        return render(request, "accounts_HTML/records.html",context=params)


#新規登録
class  AccountRegistration(TemplateView):
    def __init__(self):
        self.params = {
        "AccountCreate":False,
        "account_form": AccountForm(),
        "add_account_form":AddAccountForm(),
        }

    #Get処理
    def get(self,request):
        self.params["account_form"] = AccountForm()
        self.params["add_account_form"] = AddAccountForm()
        self.params["AccountCreate"] = False
        
        if request.user_agent.is_mobile:
            return render(request, 'accounts_mobile_HTML/register.html', self.params)
        else:
            return render(request,"accounts_HTML/register.html",context=self.params)

    #Post処理
    def post(self,request):
        self.params["account_form"] = AccountForm(data=request.POST)
        self.params["add_account_form"] = AddAccountForm(data=request.POST, files=request.FILES)
        invitation_code = request.GET.get('code')
        inviter = request.GET.get('inviter')
        
        if Account.objects.filter(user__username=request.POST['username']).count() > 0: # User IDの重複を防ぐ
            messages.error(request, "同じUser IDがすでに登録済みです。")
            redirect(to="/register")

        #フォーム入力の有効検証
        if self.params["account_form"].is_valid() and self.params["add_account_form"].is_valid():
            # アカウント情報をDB保存
            account = self.params["account_form"].save()
            # パスワードをハッシュ化
            account.set_password(account.password)
            # ハッシュ化パスワード更新                
            account.save()

            # 下記追加情報
            # 下記操作のため、コミットなし
            add_account = self.params["add_account_form"].save(commit=False)
            # AccountForm & AddAccountForm 1vs1 紐付け
            add_account.user = account

            # 画像アップロード有無検証
            if 'account_image' in request.FILES:
                add_account.account_image = request.FILES['account_image']
                print(request.FILES['account_image'], type(request.FILES['account_image']))
                msg = add_account.img_validation()
                # if msg != None:
                    # messages.error(request, msg)
                    # return redirect(to="/register")
                add_account.transform()
                
                
            # モデル保存
            add_account.save()
            
            # LINE登録用SecretKey発行
            new_account = Account.objects.filter(user__username=request.POST['username']).first()
            new_account.generate_secret_key()
            new_account.save()
            
            # 招待コードがある場合、グループに追加
            if invitation_code != None:
                print("this is an invited user.")
                # inviterの友達に設定
                (public_user, public_group) = get_public()
                frd = Companion()
                frd.owner = Account.objects.get(user__username=inviter)
                frd.user = Account.objects.get(user__username=request.POST['username'])
                frd.group = public_group
                frd.save()
                # groupに追加
                grp = Group.objects.get(invitation_code=invitation_code)
                grp.member.add(frd)
                # lineに通知
                line_notification(frd.user, group=grp, att="group")

            
            # アカウント作成情報更新
            self.params["AccountCreate"] = True
            messages.success(request, "Registered!")
            return redirect(to="/profile") # アカウント連携のページへ遷移

        else:
            # フォームが有効でない場合
            print(self.params["account_form"].errors)

        if request.user_agent.is_mobile:
            return render(request, 'accounts_mobile_HTML/register.html', self.params)
        else:
            return render(request,"accounts_HTML/register.html",context=self.params)

# Account連携のページ
@login_required
def link(request):
    user = Account.objects.get(user=request.user)
    params = {"login_user": user}
    if request.user_agent.is_mobile:
        return render(request, 'accounts_mobile_HTML/link.html', params)
    else:
        return render(request,"accounts_HTML/link.html", params)
    
    
# 登録済みプロフィールの編集
@login_required
def Profile(request):
    account = Account.objects.filter(user=request.user).first()
    print(account.account_image)
    print("/", account.icon_image)
    # POST送信時の処理
    if (request.method == 'POST'):
        reviced = AddAccountForm(request.POST, request.FILES, instance=account)
        if (reviced.is_valid()):
            # 画像アップロード有無検証
            if 'account_image' in request.FILES:    
                # reviced.account_image = request.FILES['account_image']
                account.account_image = reviced.account_image
                msg = account.img_validation()
                # if msg != None:
                    # messages.error(request, msg)
                    # return redirect(to="/profile")
                account.transform()
            print('checking...3')        
            reviced.save()
            messages.success(request, "Edit completed!")
            return redirect(to='/home')
    # GETアクセス時の処理
    else:
        reviced = AddAccountForm(instance=account)
    # 共通処理
    params = {
        "login_user": account,
        "form": reviced,
        "img_path": account.icon_image.url
    }
    if request.user_agent.is_mobile:
        return render(request, 'accounts_mobile_HTML/profile.html', params)
    else:
        return render(request, 'accounts_HTML/profile.html', params)

@login_required
def contact(request):
    user = Account.objects.filter(user=request.user).first()
    params={"login_user": user}
    if request.user_agent.is_mobile:
        return render(request, 'accounts_mobile_HTML/contact.html', params)
    else:
        return render(request, 'accounts_HTML/contact.html', params)

@login_required
def forum(request):
    user = Account.objects.filter(user=request.user).first()
    # POST
    if request.method == 'POST':
        # フォームの用意
        groupcheckform = GroupCheckForm(user, request.POST)
        # groupタイトルの取得
        glist = []
        for item in request.POST.getlist('groups'):
            glist.append(item)
        # post-itを取得
        postit = get_postit(user, glist)
    # GET
    else:
        # フォームの用意
        groupcheckform = GroupCheckForm(user)
        # post-itを取得
        postit = get_postit(user)
    # 共通
    pgenre = [genre[0] for genre in all_paper_genres]
    bgenre = [genre[0] for genre in all_genres]
    mgenre = [genre[0] for genre in all_movie_genres]
    agenre = [genre[0] for genre in all_article_genres]
    params = {
        "login_user":user,
        "contents": postit,
        "groupform": groupcheckform,
        "pgenre": pgenre,
        "bgenre": bgenre,
        "mgenre": mgenre,
        "agenre": agenre,
        }
    if request.user_agent.is_mobile:
            return render(request, 'accounts_mobile_HTML/forum.html', params)
    else:
        return render(request, "accounts_HTML/forum.html",context=params)

# 以降は普通の関数=====================================================================

# userのレコードをすべて取得
def get_records(user, page):
    page_num = 8 # 1ページあたりの表示数
    # userが作成したグループを取得
    companions = Companion.objects.filter(user=user) # userとして登録されているCompanion
    (public_user, public_group) = get_public()
    my_groups = Group.objects.filter(Q(owner=user)|Q(member__in=companions)|Q(title=public_group.title))
    bookrecords = BookRecord.objects.filter(group__in=my_groups).filter(genre__in=[item[0] for item in all_genres])
    paperrecords = PaperRecord.objects.filter(group__in=my_groups)
    movierecords = MovieRecord.objects.filter(group__in=my_groups)
    articlerecord = ArticleRecord.objects.filter(group__in=my_groups)
    all_records = list(bookrecords) + list(paperrecords) + list(movierecords) + list(articlerecord)
    if len(all_records) > 0:
        print(all_records[0].pub_date)
    sorted_records = sorted(all_records, key=lambda x:x.pub_date)
    sorted_records.reverse()
    print("all_records: ", sorted_records)
    
    page_item = Paginator(sorted_records, page_num)
    return page_item.get_page(page)

def get_friend_records(user, page, friend):
    page_num = 12 # 1ページあたりの表示数
    # userが作成したグループを取得
    companions = Companion.objects.filter(user=user) # userとして登録されているCompanion
    (public_user, public_group) = get_public()
    my_groups = Group.objects.filter(Q(owner=user)|Q(member__in=companions)|Q(title=public_group.title))
    # レコードを取得
    bookrecords = BookRecord.objects.filter(Q(owner=friend), Q(group__in=my_groups))
    paperrecords = PaperRecord.objects.filter(Q(owner=friend), Q(group__in=my_groups))
    movierecords = MovieRecord.objects.filter(Q(owner=friend), Q(group__in=my_groups))
    articlerecords = ArticleRecord.objects.filter(Q(owner=friend), Q(group__in=my_groups))
    all_records = list(bookrecords) + list(paperrecords) + list(movierecords) + list(articlerecords)
    if len(all_records) > 0:
        print(all_records[0].pub_date)
    sorted_records = sorted(all_records, key=lambda x:x.pub_date)
    sorted_records.reverse()
    print("all_records: ", sorted_records)
    page_item = Paginator(sorted_records, page_num)
    return page_item.get_page(page)

def get_proper_records(user, page, glist=[], alist=[]):
    page_num = 8
    if alist == []: # appsのチェックがないとき、すべてのアプリを選択したに等しい
        alist = ["Articles", "Books", "Movies", "Papers"]
    if glist == []: # groupsのチェックがないとき、ユーザーが所属するすべてのグループを選択したに等しい
        companions = Companion.objects.filter(user=user) # userとして登録されているCompanion
        (public_user, public_group) = get_public()
        glist = [group.title for group in Group.objects.filter(Q(owner=user)|Q(member__in=companions)|Q(title=public_group.title))]
    # glistをクエリセットに
    my_groups = Group.objects.filter(title__in=glist)
    # それぞれのアプリについて、空のクエリセットを用意
    articlerecords = ArticleRecord.objects.none()
    bookrecords = BookRecord.objects.none()
    movierecords = MovieRecord.objects.none()
    paperrecords = PaperRecord.objects.none()
    # チェックされたアプリのレコードを取得
    if "Articles" in alist:
        articlerecords = ArticleRecord.objects.filter(group__in=my_groups)
    if "Books" in alist:
        bookrecords = BookRecord.objects.filter(group__in=my_groups)
    if "Papers" in alist:
        paperrecords = PaperRecord.objects.filter(group__in=my_groups)
    if "Movies" in alist:
        movierecords = MovieRecord.objects.filter(group__in=my_groups)
    # レコードを結合
    all_records = list(bookrecords) + list(paperrecords) + list(movierecords) + list(articlerecords)
    # 投稿日時で並べ替え
    if len(all_records) > 0:
        print(all_records[0].pub_date)
    sorted_records = sorted(all_records, key=lambda x:x.pub_date)
    sorted_records.reverse()
    print("all_records: ", sorted_records)
    page_item = Paginator(sorted_records, page_num)
    return page_item.get_page(page)
        

# publicなUserとGroupを取得する
def get_public():
    public_user = Account.objects.filter(user__username='public').first()
    public_group = Group.objects.filter(owner=public_user).first()
    return (public_user, public_group)

# post-itを取得する
def get_postit(user, glist=[]):
    if glist == []: # groupsのチェックがないとき、ユーザーが所属するすべてのグループを選択したに等しい
        companions = Companion.objects.filter(user=user) # userとして登録されているCompanion
        (public_user, public_group) = get_public()
        glist = [group.title for group in Group.objects.filter(Q(owner=user)|Q(member__in=companions)|Q(title=public_group.title))]
    # glistをクエリセットに
    my_groups = Group.objects.filter(title__in=glist)
    # それぞれのアプリについて、レコードを取得
    articlerecords = ArticleRecord.objects.filter(group__in=my_groups)
    bookrecords = BookRecord.objects.filter(group__in=my_groups)
    movierecords = MovieRecord.objects.filter(group__in=my_groups)
    paperrecords = PaperRecord.objects.filter(group__in=my_groups)
    # それぞれのアプリについて、Post-itを取得
    articlechats = ArticleChat.objects.filter(record__in=articlerecords).filter(reply_id=-1)
    bookchats = Chat.objects.filter(record__in=bookrecords).filter(reply_id=-1)
    moviechats = MovieChat.objects.filter(record__in=movierecords).filter(reply_id=-1)
    paperchats = PaperChat.objects.filter(record__in=paperrecords).filter(reply_id=-1)
    # レコードを結合
    all_postit = list(bookchats) + list(paperchats) + list(moviechats) + list(articlechats)
    # 投稿日時で並べ替え
    if len(all_postit) > 0:
        print(all_postit[0].pub_date)
    sorted_postit = sorted(all_postit, key=lambda x:x.pub_date)
    sorted_postit.reverse()
    return sorted_postit

def get_one_record(user):
    # userが作成したグループを取得
    companions = Companion.objects.filter(user=user) # userとして登録されているCompanion
    (public_user, public_group) = get_public()
    my_groups = Group.objects.filter(Q(owner=user)|Q(member__in=companions)|Q(title=public_group.title))
    bookrecords = BookRecord.objects.filter(group__in=my_groups).filter(genre__in=[item[0] for item in all_genres])
    paperrecords = PaperRecord.objects.filter(group__in=my_groups)
    movierecords = MovieRecord.objects.filter(group__in=my_groups)
    articlerecord = ArticleRecord.objects.filter(group__in=my_groups)
    all_records = list(bookrecords) + list(paperrecords) + list(movierecords) + list(articlerecord)
    # ランダムにレコードを抽出
    record = random.choice(all_records)
    return record

def user_engagement(user, date=datetime.date.today()):
    # 投稿数をn_recordsに格納
    n_records = BookRecord.objects.filter(Q(owner=user)&Q(pub_date__lte=date)).count() + PaperRecord.objects.filter(Q(owner=user)&Q(pub_date__lte=date)).count() + ArticleRecord.objects.filter(Q(owner=user)&Q(pub_date__lte=date)).count() + MovieRecord.objects.filter(Q(owner=user)&Q(pub_date__lte=date)).count()
    # コメント数をn_postitに格納
    n_comment = Chat.objects.filter(Q(owner=user)&Q(pub_date__lte=date)).count() + PaperChat.objects.filter(Q(owner=user)&Q(pub_date__lte=date)).count() + ArticleChat.objects.filter(Q(owner=user)&Q(pub_date__lte=date)).count() + MovieChat.objects.filter(Q(owner=user)&Q(pub_date__lte=date)).count()
    return n_records, n_comment

def create_graph(n_records, n_comments ,months):
    plt.cla()
    fig, ax = plt.subplots(figsize=(5,5))
    fig.set_facecolor("#002A3E")
    ax.set_facecolor("#002A3E")
    plt.plot(months, n_records, marker="o", label="records", color=("#FF9900", 0.5))
    plt.plot(months, n_comments, marker="x", label="comments", color=("#FFCC33", 0.5))
    plt.xlabel('month')
    plt.xticks(rotation=30, color="white")
    plt.ylabel('')
    plt.yticks(color="white")
    plt.legend(facecolor="#002A3E", edgecolor="#002A3E", labelcolor="white")
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    

def get_image():
 buffer = io.BytesIO()
 plt.savefig(buffer, format='png')
 image_png = buffer.getvalue()
 graph = base64.b64encode(image_png)
 graph = graph.decode('utf-8')
 buffer.close()
 return graph