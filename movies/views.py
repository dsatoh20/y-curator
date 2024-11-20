from django.shortcuts import render
from django.shortcuts import redirect
from accounts.models import Account
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .models import MovieRecord, MovieChat
from books.models import BookRecord, Friend, Group, Good, Chat, Companion
from books.forms import BookRecordForm, GroupCheckForm, GroupSelectForm, \
    FriendsForm, CreateGroupForm, PostForm, GenreSelectForm,\
        FindUserForm, CompanionsForm
from books.forms import all_genres
from .forms import PostMovieForm, MovieGenreSelectForm, MovieRecordForm, ChatForm, ReplyForm
from .forms import all_movie_genres
from books.views import line_notification

onerror = "this.onerror=null;this.src='data:image/svg+xml;base64,\
    PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPS\
        IyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij48cGF0aCBkP\
            SJNNSA4LjVjMC0uODI4LjY3Mi0xLjUgMS41LTEuNXMxLjUuNjcyIDEuN\
                SAxLjVjMCAuODI5LS42NzIgMS41LTEuNSAxLjVzLTEuNS0uNjcxLT\
                    EuNS0xLjV6bTkgLjVsLTIuNTE5IDQtMi40ODEtMS45Ni00IDUuO\
                        TZoMTRsLTUtOHptOC00djE0aC0yMHYtMTRoMjB6bTItMmgtM\
                            jR2MThoMjR2LTE4eiIvPjwvc3ZnPg==';"



# indexのビュー関数
@login_required(login_url='/')
def index(request, page=1):
    # login中のuserを取り出す
    user = Account.objects.get(user=request.user)
    # publicのuserを取得
    (public_user, public_group) = get_public()
    # POST
    if request.method == 'POST':
        checkform = GroupCheckForm(user, request.POST)
        glist = []
        genlist = []
        for item in request.POST.getlist('groups'):
            glist.append(item)
        if "-" in glist:
            companions = Companion.objects.filter(user=user)
            gps = Group.objects.filter(Q(owner=user)|Q(member__in=companions)).distinct() # 自分がownerのグループ or 自分がmemberに追加されているグループ
            glist = [public_group.title]
            for item in gps:
                glist.append(item.title)
        for item in request.POST.getlist('genre'):
            genlist.append(item)
        if glist == []:
            gps = Group.objects.filter(owner=user)
            glist = [public_group.title]
            for item in gps:
                glist.append(item.title)
        if genlist == ['-']:
            genlist = [item[0] for item in all_movie_genres]
        movierecord = get_your_group_movierecord(user, glist, genlist, page)
    # GETアクセス時の処理
    else:
        # フォームの用意
        checkform = GroupCheckForm(user)
        # Groupのリストを取得
        companions = Companion.objects.filter(user=user)
        gps = Group.objects.filter(Q(owner=user)|Q(member__in=companions)).distinct() # 自分がownerのグループ or 自分がmemberに追加されているグループ
        glist = [public_group.title]
        for item in gps:
            glist.append(item.title)
        # Genreのリストを取得
        genlist = [item[0] for item in all_movie_genres]
        # MovieRecordの取得
        movierecord = get_your_group_movierecord(user, glist, genlist, page)
    # 共通
    genreform = MovieGenreSelectForm()
    params={
        'login_user': user,
        'contents': movierecord,
        'check_form': checkform,
        'gen_form': genreform,
        'onerror': onerror,
    }
    if request.user_agent.is_mobile:
        return render(request, 'movies_mobile_HTML/index.html', params)
    else:
        return render(request, "movies_HTML/index.html", params)

# MovieRecordのポスト
@login_required(login_url='/')
def post(request):
    # login中のuserを取り出す
    user = Account.objects.get(user=request.user)
    # POST送信の処理
    if request.method == 'POST':
        # 送信内容の処理
        form = PostMovieForm(user, request.POST)
        gr_name = request.POST['group']
        title = request.POST['title']
        director = request.POST['director']
        pub_year = request.POST['pub_year']
        genre = request.POST['genre']
        score = request.POST['score']
        summary = request.POST['summary']
        report = request.POST['report']
        if (form.is_valid()):
            # Groupの取得
            group = Group.objects.filter(title=gr_name).first()
            if group == None:
                (pub_user, group) = get_public()
            # MovieRecordを作成して保存
            prcd = MovieRecord()
            prcd.owner = user
            prcd.group = group
            prcd.title = title
            prcd.director = director
            prcd.pub_year = pub_year
            print(genre=='-')
            if genre == '-' or genre == ('-', '-'):
                genre = ''
            prcd.genre = genre
            prcd.score = score
            prcd.summary = summary
            prcd.report = report
            prcd.auto_fill()
            prcd.save()
            line_notification(user, group, att="post", url=f"/movies/chat/{prcd.id}", record=prcd) # LINEに通知
            print("MovieRecordポスト成功")
            # メッセージを設定
            messages.success(request, '新しいRecordを投稿しました！')
            return redirect(to='/home')
    
    # GETアクセス時の処理
    else:
        form = PostMovieForm(user)
    # 共通処理
    params = {
        'login_user': user,
        'form': form,
    }
    if request.user_agent.is_mobile:
        return render(request, 'movies_mobile_HTML/post.html', params)
    else:
        return render(request, "movies_HTML/post.html", params)


# chatボタンの処理
@login_required(login_url='/')
def chat_button(request, chat_id):
    # chatするMovieRecordを取得
    chat_prcd = MovieRecord.objects.get(id=chat_id)
    messages.success(request, 'Chatページに移行します！')
    return redirect(to="/movies/chat.html")

# chatのビュー関数
@login_required(login_url='/')
def chat(request, chat_id):
    # login中のuserを取り出す
    user = Account.objects.get(user=request.user)
    chat_theme = MovieRecord.objects.get(id=chat_id)
    # 閲覧権があるかチェック なければTOPへ戻る
    group = chat_theme.group
    if group.title == 'public':
        pass
    else:
        members = group.member.all()
        member_names = [member.user.user.username for member in members]
        if (user.user.username not in member_names) and (user.user.username != group.owner.user.username):
            messages.error(request, "メンバーに登録されていません。")
            return redirect(to="/movies")
    # POST送信時の処理
    if request.method == 'POST':
        # 送信内容の処理
        comment = request.POST['comment']
        # Chatを作成して保存
        chat = MovieChat()
        chat.owner = user
        chat.record = chat_theme
        chat.comment = comment
        chat.save()
        # MovieRecordのchat_countを1増やす
        # num = Chat.objects.filter(Movierecord=chat_theme).count()
        chat_theme.chat_count += 1
        # chat_theme.chat_count = num
        chat_theme.save()
        line_notification(user, chat_theme.group, att="comment", url=f"/movies/chat/{chat_id}", record=chat_theme) # LINEに通知
        print("POST OK")
        print("リプIDは、", chat.reply_id)
        messages.success(request, "コメントしました。")
        
    # GETアクセス時の処理
    else:
        pass
    # 共通処理
    user.get_history(app="Movies", record=chat_theme)
    user.save()
    form = ChatForm()
    chat = MovieChat.objects.filter(record=chat_theme).filter(reply_id__lt = 0)
    reply = MovieChat.objects.filter(record=chat_theme).filter(reply_id__gt = 0)
    params = {
        'login_user': user,
        'prcd_contents': chat_theme,
        'chat_contents': chat,
        'reply_contents':reply,
        'form': form,
        'id': chat_id,
        'img_path': chat_theme.img_path,
        'onerror': onerror,
    }
    if request.user_agent.is_mobile:
        return render(request, 'movies_mobile_HTML/chat.html', params)
    else:
        return render(request, 'movies_HTML/chat.html', params)

from books.insertTag import insert_tag
# highlightした文字列にコメント
@login_required(login_url='/')
def highlight(request, highlight_id):
    # login中のuserを取り出す
    user = Account.objects.get(user=request.user)
    chat_theme = MovieRecord.objects.get(id=highlight_id)
    comment = request.POST['highlight']
    spaceless = comment.replace(' ', '').replace('\n', '')
    if spaceless == "" or spaceless == None:
        messages.error(request, "カーソルで文字列を選択してください。")
        return redirect(to=f'/movies/chat/{highlight_id}')
    # Chatを作成して保存
    chat = MovieChat()
    chat.owner = user
    chat.record = chat_theme
    chat.comment = comment
    chat.save()
    # 感想を述べたい文章を選択しただけなので、カウントは増やさない
    # chat_theme.chat_count += 1
    chat_theme.save()
    print("ハイライトをコメント化成功")
    # line_notification(user, chat_theme.group, att="comment") # LINEに通知
    # messages.success(request, "コメントしました。")
    insert_tag(highlight_id, chat_theme, comment, chat.id, app="movies") # ユーザーが選択した文字列をリンクにする
    
    # return redirect(to=f"/books/chat/{highlight_id}/reply/{reply_id}")
    return redirect(to=f'/movies/chat/{highlight_id}/reply/{chat.id}')

@login_required(login_url="/")
def reply(request, chat_id, reply_id):
    # ログイン中のユーザーを取得
    user = Account.objects.get(user=request.user)
    # リプライするチャットを取得
    chat = MovieChat.objects.get(id=reply_id)
    # チャットテーマとなるレコードを取得
    chat_theme = chat.record
    # チャットへのリプライをすべて取得
    replies = MovieChat.objects.filter(record=chat.record).filter(reply_id__gt = 0).filter(reply_id=chat.id)
    # 閲覧権があるかチェック なければTOPへ戻る
    group = chat_theme.group
    if group.title == 'public':
        pass
    else:
        members = group.member.all()
        member_names = [member.user.user.username for member in members]
        if (user.user.username not in member_names) and (user.user.username != group.owner.user.username):
            messages.error(request, "メンバーに登録されていません。")
            return redirect(to="/movies")
    # POST
    if request.method == 'POST':
        rep_comment = request.POST.get('comment')
        print("リプライ入りました", rep_comment)
        reply = MovieChat()
        # if (reply.is_valid()):                
        reply.owner = user
        reply.record = chat.record
        reply.comment = rep_comment
        reply.reply_id = chat.id # chatとreplyの対応
        reply.save()
        print("リプIDは、", reply.reply_id)
        messages.success(request, "リプライしました。")
        # chat_countを1増やす
        chat_theme.chat_count += 1
        chat_theme.save()
        # reply_countを1増やす
        chat.reply_count += 1
        chat.save()
        line_notification(user, chat_theme.group, att="comment", url=f"/movies/chat/{chat_id}/reply/{reply_id}", record=chat_theme) # LINEに通知
        # else:
            # messages.error(request, "validation error occured.")
    # GET
    else:
        pass
    # 共通
    params = {
        'login_user': user,
        'prcd_contents': chat_theme,
        'chat_contents': chat,
        'reply_contents': replies,
        'chat_id': chat_id,
        'reply_id': reply_id,
        'form': ReplyForm(),    
        'img_path': chat_theme.img_path,
        'onerror': onerror, 
    }
    if request.user_agent.is_mobile:
        return render(request, 'movies_mobile_HTML/reply.html', params)
    else:
        return render(request, "movies_HTML/reply.html", params)
    

# Editのビュー関数   
@login_required(login_url="/") 
def edit(request, edit_id):
    # login中のuserを取り出す
    user = Account.objects.get(user=request.user)
    prcd = MovieRecord.objects.get(id=edit_id)
    pre_list = [prcd.group, prcd.genre, prcd.pub_year, prcd.director, prcd.score, prcd.summary, prcd.report]
    if prcd.owner != user:
        messages.success(request, '自分のでないレコードは編集できません。')
        return redirect(to=f'/movies/chat/{edit_id}')
    # POST送信時の処理
    if (request.method == 'POST'):
        reviced = MovieRecordForm(request.POST, instance=prcd)
        group_form = GroupSelectForm(user, request.POST)
        rev_group = request.POST.get("groups")
        genre_form = MovieGenreSelectForm(request.POST)
        rev_genre = request.POST.get("genre")
        if (reviced.is_valid() and group_form.is_valid() and genre_form.is_valid()):
            prcd.genre = rev_genre
            prcd.group = Group.objects.get(title=rev_group)
            prcd.save()
            reviced.save()
            post_list = [prcd.group, prcd.genre, prcd.pub_year, prcd.director, prcd.score, prcd.summary, prcd.report]
            if post_list == pre_list: # まったく編集せずPOST!をクリックした場合
                return redirect(to=f'/movies/chat/{edit_id}') # edit_dateは更新されてしまうが、edit_countは更新されない
            prcd.edit_count += 1
            prcd.save()
            return redirect(to=f'/movies/chat/{edit_id}')
    # GETアクセス時の処理
    else:
        reviced = MovieRecordForm(instance=prcd)
        genre_form = MovieGenreSelectForm({"genre": prcd.genre})
        group_form = GroupSelectForm(user, {"groups": prcd.group.title})
    # 共通処理
    params = {
        'login_user': user,
        'id': edit_id,
        'form': reviced,
        'genre_form': genre_form,
        'group_form': group_form,
        'prcd': prcd,
    }
    if request.user_agent.is_mobile:
        return render(request, 'movies_mobile_HTML/edit.html', params)
    else:
        return render(request, 'movies_HTML/edit.html', params)
# Repostのビュー関数   
@login_required(login_url="/") 
def repost(request, repost_id):
    # login中のuserを取り出す
    user = Account.objects.get(user=request.user)
    brcd = MovieRecord.objects.get(id=repost_id)
    if brcd.owner != user:
        messages.success(request, '自分のでないレコードはリポストできません。')
        return redirect(to=f'/movies/chat/{repost_id}')
    # POST送信時の処理
    if (request.method == 'POST'):
        repost = MovieRecord()
        reviced = MovieRecordForm(request.POST, instance=brcd)
        group_form = GroupSelectForm(user, request.POST)
        rev_group = request.POST.get("groups")
        genre_form = MovieGenreSelectForm(request.POST)
        rev_genre = request.POST.get("genre")
        
        if (reviced.is_valid() and group_form.is_valid() and genre_form.is_valid()):
            repost.genre = rev_genre
            repost.group = Group.objects.get(title=rev_group)
            repost.owner = user
            repost.title = brcd.title
            repost.director = request.POST['director']
            repost.img_path = brcd.img_path
            repost.pub_year = request.POST['pub_year']
            repost.score = request.POST['score']
            repost.summary = request.POST['summary']
            repost.report = request.POST['report']
            if repost.group == brcd.group:
                messages.error(request, 'もとのレコードと同じGroupが選択されています。')
                return redirect(to=f'/movies/repost/{repost_id}')
            repost.save()
            messages.success(request, 'レコードをリポストしました！')
            return redirect(to='/home')
        
    # GETアクセス時の処理
    else:
        reviced = MovieRecordForm(instance=brcd)
        genre_form = MovieGenreSelectForm({"genre": brcd.genre})
        group_form = GroupSelectForm(user, {"groups": brcd.group.title})
    # 共通処理
    params = {
        'login_user': user,
        'id': repost_id,
        'form': reviced,
        'genre_form': genre_form,
        'group_form': group_form,
        'brcd': brcd,
    }
    if request.user_agent.is_mobile:
        return render(request, 'movies_mobile_HTML/repost.html', params)
    else:
        return render(request, 'movies_HTML/repost.html', params)

# Deleteのビュー関数
@login_required(login_url="/")
def delete(request, del_id):
    # login中のuserを取り出す
    user = Account.objects.get(user=request.user)
    prcd = MovieRecord.objects.get(id=del_id)
    if prcd.owner != user:
        messages.success(request, "自分のでないレコードは削除できません")
        return redirect(to=f'/movies/chat/{del_id}')
    # POST送信時の処理
    if (request.method == 'POST'):
        prcd.delete()
        chats = MovieChat.objects.filter(record=prcd)
        for chat in chats:
            chat.delete()
        messages.success(request, 'レコードを削除しました。')
        return redirect(to='/home')
    # GETアクセス時の処理
    # 共通処理
    params = {
        'login_user': user,
        'id': del_id,
        'contents': prcd,
    }
    if request.user_agent.is_mobile:
        return render(request, 'movies_mobile_HTML/delete.html', params)
    else:
        return render(request, 'movies_HTML/delete.html', params)

# 以降は普通の関数=====================================================================

def get_your_group_movierecord(owner, glist, genlist, page):
    page_num = 8 # ページ当たりの表示数
    # publicの取得
    (public_user, public_group) = get_public()
    # チェックされたGroupの取得
    groups = Group.objects.filter(title__in=glist)
    # Groupがgroupsかme_groupsに含まれるMovieRecordの取得
    movierecords = MovieRecord.objects.filter(group__in=groups).filter(genre__in=genlist).distinct()
    # ページネーションで指定ページを取得
    page_item = Paginator(movierecords, page_num)
    return page_item.get_page(page)

    
# publicなUserとGroupを取得する
def get_public():
    public_user = Account.objects.filter(user__username='public').first()
    public_group = Group.objects.filter(owner=public_user).first()
    return (public_user, public_group)
