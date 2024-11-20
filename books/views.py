from django.shortcuts import render
from django.shortcuts import redirect
from accounts.models import Account
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .models import BookRecord, Friend, Group, Good, Chat, Companion
from .forms import BookRecordForm, GroupCheckForm, GroupSelectForm, \
    FriendsForm, CreateGroupForm, PostForm, ChatForm, ReplyForm, GenreSelectForm,\
        FindUserForm, CompanionsForm
from .forms import all_genres
from books.push import SendMsg
from books.insertTag import insert_tag
from linebots.bot_messages import create_message
from linebots.views import homepage_link

import json, os
from cryptography.fernet import Fernet

try:
    with open('linebots/conf.json', 'r') as f:
        data = json.load(f)
    fernet = Fernet(data["SECRET_KEY"])
except:
    fernet = Fernet(os.environ.get("SECRET_KEY"))
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
    
    # POST送信時の処理
    """
    if request.method == 'POST':
        
        # Groupsのチェックを更新したときの処理
        # フォームの用意
        checkform = GroupCheckForm(request.user, request.POST)
        # チェックされたGroup名をリストにまとめる
        glist = []
        for item in request.POST.getlist('groups'):
            glist.append(item)
        # BookRecordの取得
        bookrecord = get_your_group_bookrecord(request.user, glist, page)
    """
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
            genlist = [item[0] for item in all_genres]
        bookrecord = get_your_group_bookrecord(user, glist, genlist, page)
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
        genlist = [item[0] for item in all_genres]
        # BookRecordの取得
        bookrecord = get_your_group_bookrecord(user, glist, genlist, page)
    
    # 共通処理
    genreform = GenreSelectForm()
    params = {
        'login_user': user,
        'contents': bookrecord,
        'check_form': checkform,
        'gen_form': genreform,
        'onerror': onerror,
    }
    if request.user_agent.is_mobile:
        return render(request, 'books_mobile_HTML/index.html', params)
    else:
        return render(request, 'books_HTML/index.html', params)

@login_required(login_url='/')
def groups(request):
    # login中のuserを取り出す
    user = Account.objects.get(user=request.user)
    # 自分が登録したFriendを取得
    friends = Companion.objects.filter(owner=user)
    print("あなたのfriendは", friends)
    
    # POST送信時の処理
    if request.method == 'POST':
        
        # Groupsメニュー選択肢の処理
        if request.POST['mode'] == '__groups_form__':
            # 選択したGroup名を取得
            sel_group = request.POST['groups']
            if sel_group == "-":
                messages.error(request, "Groupを選択してください。")
                return redirect(to="/books/groups")
            # Groupを取得
            gp = Group.objects.filter(title=sel_group).first()
            # Groupに含まれるFriendを取得
            fds = gp.member.all()
            print("Groupsメニュー選択", gp, gp.member, gp.member.all())
            # FriendのUserをリストにまとめる
            vlist = []
            for item in fds:
                vlist.append(item.user.user.username)
            # フォームの用意
            groupsform = GroupSelectForm(user, request.POST)
            friendsform = CompanionsForm(user, companions=friends, vals=vlist)
        # Friendsのチェック更新時の処理
        if request.POST['mode'] == '__friends_form__':
            # 選択したGroupを取得
            try:
                sel_group = request.POST['group']
                if sel_group == "-":
                    messages.error(request, "Groupを選択してください。")
                    return redirect(to="/books/groups")
                group_obj = Group.objects.filter(title=sel_group).first()
                # チェックしたFriendsを取得
                sel_fds = request.POST.getlist('friends')
                # 以前のメンバーを取得
                pre_mbs = group_obj.member.all()
                for item in pre_mbs:
                    if item.user.user.username not in sel_fds:
                        group_obj.member.remove(item)
                print("１", sel_fds)
                # FriendsのUserを取得
                sel_users = Account.objects.filter(user__username__in=sel_fds)
                print("２", sel_users)
                # Userのリストに含まれるユーザーが登録したFriendを取得
                fds = Companion.objects.filter(owner=user).filter(user__in=sel_users)
                print("３", fds)
                # すべてのFriendにGroupを設定し保存
                vlist = []
                if group_obj.owner == user:
                    for item in fds:
                        group_obj.member.add(item)
                        vlist.append(item.user.user.username)
                    print("４", vlist)
                    line_notification(user, group_obj, att="group")
                    # メッセージを設定
                    messages.success(request, 'チェックされたFriendを' + sel_group + 'に登録しました。')
                else:
                    for item in pre_mbs:
                        group_obj.member.add(item)
                        vlist.append(item.user.user.username)
                    messages.error(request, "グループメンバー登録はオーナーのみ行えます")
                # フォームの用意
                groupsform = GroupSelectForm(user, {'groups': sel_group})
                friendsform = CompanionsForm(user, companions=friends, vals=vlist)
            except:
                messages.success(request, "グループを選択してください。")
                groupsform = GroupSelectForm(user)
                friendsform = CompanionsForm(user, companions=friends, vals=[])
            
    # GETアクセス時の処理
    else:
        # フォームの用意
        groupsform = GroupSelectForm(user)
        friendsform = CompanionsForm(user, companions=friends, vals=[])
        sel_group = '-'
    # 共通処理
    createform = CreateGroupForm()
    params = {
        'login_user': user,
        'groups_form': groupsform,
        'friends_form': friendsform,
        'create_form': createform,
        'group': sel_group,
        'group_obj': Group.objects.filter(title=sel_group).first(),
    }
    if request.user_agent.is_mobile:
        return render(request, 'books_mobile_HTML/groups.html', params)
    else:
        return render(request, 'books_HTML/groups.html', params)
    
# Friendの追加処理
@login_required(login_url='/')
def add(request):
    # login中のuserを取り出す
    user = Account.objects.get(user=request.user)
    # 追加するUserを取得
    add_name = request.GET['name']
    add_user = Account.objects.filter(user__username=add_name).first()
    # Userが本人だった場合の処理
    if add_user == user:
        messages.info(request, "自分自身をFriendに追加することはできません。")
        return redirect(to='/books/friend')
    # publicの取得
    (public_user, public_group) = get_public()
    # add_userのFriendの数を調べる
    frd_num = Companion.objects.filter(owner=user).filter(user=add_user).count()
    # ゼロより大きければすでに登録済み
    if frd_num > 0:
        messages.info(request, add_user.user.username + 'は既に追加されています。')
        return redirect(to='/books/friend')
    # ここからFriendの登録処理
    else:
        frd = Companion()
        frd.owner = user
        frd.user = add_user
        frd.group = public_group
        frd.save()
        line_notification(user, public_group, att="friend", friend=frd)
        # メッセージを設定
        messages.success(request, add_user.user.username + 'を追加しました！\
            groupページに移動して、' + add_user.user.username + 'をメンバーに設定してください。')
        return redirect(to='/books/friend')
    
# フレンドページビュー
@login_required(login_url='/')
def friend(request):
    # login中のuserを取り出す
    user = Account.objects.get(user=request.user)
    # publicの取得
    (public_user, public_group) = get_public()
    # 以前からのfriendを取得
    friend_list = Companion.objects.filter(owner=user)
    # POST送信時の処理
    if request.method == 'POST':
        if request.POST['mode'] == '__find_form__':
            # friend候補をメールアドレスで検索
            form = FindUserForm(request.POST)
            gform = GroupSelectForm(user)
            find = request.POST['find']        
            data = Account.objects.filter(email=find)
            msg = 'Result: ' + str(data.count()) # 検索ヒット数を表示
        elif request.POST['mode'] == '__group_form__':
            # groupメンバーを表示
            form = FindUserForm()
            gform = GroupSelectForm(user, request.POST)
            group_title = request.POST['groups']
            if gform.is_valid():
                group = Group.objects.get(title=group_title)
                members = group.member.all()
                member_list = []
                for member in members:
                    name = member.user.user.username
                    member_list.append(name)
                member_list.append(group.owner.user.username)
                data = Account.objects.filter(user__username__in=member_list)
                msg = str(group.title) + 'メンバー数: ' + str(data.count()) # 検索ヒット数を表示
            else:
                msg = "Groupを選択してください。"
                data = None
    # GETアクセス時の処理
    else:
        msg = "search user..."
        form = FindUserForm()
        cdata = Companion.objects.filter(owner=user)
        data = [item.user for item in cdata]
        gform = GroupSelectForm(user)
    params = {
        'title': 'Friend',
        'login_user': user,
        'message': msg,
        'form': form,
        'gform': gform,
        'data': data,
    }
    if request.user_agent.is_mobile:
        return render(request, 'books_mobile_HTML/friend.html', params)
    else:
        return render(request, 'books_HTML/friend.html', params)

# グループの作成処理
@login_required(login_url='/')
def creategroup(request):
    # login中のuserを取り出す
    user = Account.objects.get(user=request.user)
    # Groupを作り、Userとtitleを設定して保存
    gp = Group()
    gp.owner = user
    gp.title = user.user.username + 'の' + request.POST['group_name']
    gp.generate_invitation_code()
    gp.save()
    messages.info(request, '新しいグループを作成しました。')
    return redirect(to='/books/groups')
    
    
# 読書記録のポスト処理
@login_required(login_url='/')
def post(request):
    # login中のuserを取り出す
    user = Account.objects.get(user=request.user)
    # POST送信の処理
    if request.method == 'POST':
        # 送信内容の処理
        form = PostForm(user, request.POST)
        gr_name = request.POST['group']
        # isbn = request.POST['isbn']
        isbn = ""
        title = request.POST['title']
        first_author = request.POST['first_author']
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
            # BookRecordを作成して保存
            brcd = BookRecord()
            brcd.owner = user
            brcd.group = group
            brcd.isbn = isbn
            brcd.title = title
            brcd.first_author = first_author
            brcd.pub_year = pub_year
            brcd.genre = genre
            brcd.score = score
            brcd.summary = summary
            brcd.report = report
            if isbn != '' or isbn != None:
                brcd.rm_hyphen() # 入力されたISBNからハイフンを削除
            try:
                brcd.auto_fill()
                messages.warning(request, '書籍情報の取得に成功しました。detailsから確認してください')
            except:
                print("xxxxxxxx")
                messages.error(request, "書籍情報の取得に失敗しました。Editから手動で入力してください")
            brcd.save()
            # GroupメンバーのLINEに通知
            line_notification(user, group, att="post", url=f"/books/chat/{brcd.id}", record=brcd)
            # メッセージを設定
            messages.success(request, '新しいRecordを投稿しました！')
            return redirect(to='/home')
        

    
    # GETアクセス時の処理
    else:
        form = PostForm(user)
    # 共通処理
    params = {
        'login_user': user,
        'form': form,
    }
    if request.user_agent.is_mobile:
        return render(request, 'books_mobile_HTML/post.html', params)
    else:
        return render(request, 'books_HTML/post.html', params)

# goodボタンの処理
@login_required(login_url='/')
def good(request, good_id):
    # goodするBookRecordを取得
    good_brcd = BookRecord.objects.get(id=good_id)
    # 自分がメッセージにGoodした数を調べる
    is_good = Good.objects.filter(owner=user).filter(record=good_brcd).count()
    # ゼロより大きければすでにgood済み
    if is_good > 0:
        messages.success(request, 'すでにメッセージにはGoodしています。')
        return redirect(to='/home')
    
    # BookRecordのgood_countを1増やす
    good_brcd.good_count += 1
    good_brcd.save()
    # Goodを作成し、設定して保存
    good = Good()
    good.owner = user
    good.record = good_brcd
    good.save()
    # メッセージを設定
    messages.success(request, 'RecordにGoodしました！')
    return redirect(to='/home')

# chatボタンの処理
@login_required(login_url='/')
def chat_button(request, chat_id):
    # chatするBookRecordを取得
    chat_brcd = BookRecord.objects.get(id=chat_id)
    messages.success(request, 'Chatページに移行します！')
    return redirect(to="/books/chat.html")

# chatのビュー関数
@login_required(login_url='/')
def chat(request, chat_id):
    # login中のuserを取り出す
    user = Account.objects.get(user=request.user)
    chat_theme = BookRecord.objects.get(id=chat_id)
    # 閲覧権があるかチェック なければTOPへ戻る
    group = chat_theme.group
    if group.title == 'public':
        pass
    else:
        members = group.member.all()
        member_names = [member.user.user.username for member in members]
        if (user.user.username not in member_names) and (user.user.username != group.owner.user.username):
            messages.error(request, "メンバーに登録されていません。")
            return redirect(to="/home")
    # POST送信時の処理
    if request.method == 'POST':
        # 送信内容の処理
        comment = request.POST['comment']
        # Chatを作成して保存
        chat = Chat()
        chat.owner = user
        chat.record = chat_theme
        chat.comment = comment
        chat.save()
        # BookRecordのchat_countを1増やす
        # num = Chat.objects.filter(bookrecord=chat_theme).count()
        chat_theme.chat_count += 1
        # chat_theme.chat_count = num
        chat_theme.save()
        print("POST OK")
        print("リプIDは、", chat.reply_id)
        line_notification(user, chat_theme.group, att="comment", url=f"/books/chat/{chat_id}", record=chat_theme) # LINEに通知
        messages.success(request, "コメントしました。")
        
    # GETアクセス時の処理
    else:
        pass
    # 共通処理
    user.get_history(app="Books", record=chat_theme)
    user.save()
    form = ChatForm()
    chat = Chat.objects.filter(record=chat_theme).filter(reply_id__lt = 0)
    reply = Chat.objects.filter(record=chat_theme).filter(reply_id__gt = 0)
    params = {
        'login_user': user,
        'brcd_contents': chat_theme,
        'chat_contents': chat,
        'reply_contents':reply,
        'form': form,
        'id': chat_id,
        'img_path': chat_theme.isbn,
        'onerror': onerror,
    }
    if request.user_agent.is_mobile:
        return render(request, 'books_mobile_HTML/chat.html', params)
    else:
        return render(request, 'books_HTML/chat.html', params)
# highlightした文字列にコメント
@login_required(login_url='/')
def highlight(request, highlight_id):
    # login中のuserを取り出す
    user = Account.objects.get(user=request.user)
    chat_theme = BookRecord.objects.get(id=highlight_id)
    comment = request.POST['highlight']
    spaceless = comment.replace(' ', '').replace('\n', '')
    if spaceless == "" or spaceless == None:
        messages.error(request, "カーソルで文字列を選択してください。")
        return redirect(to=f'/books/chat/{highlight_id}')
    # Chatを作成して保存
    chat = Chat()
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
    insert_tag(highlight_id, chat_theme, comment, chat.id, app="books") # ユーザーが選択した文字列をリンクにする
    
    # return redirect(to=f"/books/chat/{highlight_id}/reply/{reply_id}")
    return redirect(to=f'/books/chat/{highlight_id}/reply/{chat.id}')
    

@login_required(login_url="/")
def reply(request, chat_id, reply_id):
    # ログイン中のユーザーを取得
    user = Account.objects.get(user=request.user)
    # リプライするチャットを取得
    chat = Chat.objects.get(id=reply_id)
    # チャットテーマとなるレコードを取得
    chat_theme = chat.record
    # チャットへのリプライをすべて取得
    replies = Chat.objects.filter(record=chat.record).filter(reply_id__gt = 0).filter(reply_id=chat.id)
    # 閲覧権があるかチェック なければTOPへ戻る
    group = chat_theme.group
    if group.title == 'public':
        pass
    else:
        members = group.member.all()
        member_names = [member.user.user.username for member in members]
        if (user.user.username not in member_names) and (user.user.username != group.owner.user.username):
            messages.error(request, "メンバーに登録されていません。")
            return redirect(to="/home")
    # POST
    if request.method == 'POST':
        rep_comment = request.POST.get('comment')
        print("リプライ入りました", rep_comment)
        reply = Chat()
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
        line_notification(user, chat_theme.group, att="comment", url=f"/books/chat/{chat_id}/reply/{reply_id}", record=chat_theme) # LINEに通知
        # else:
            # messages.error(request, "validation error occured.")
    # GET
    else:
        pass
    # 共通
    params = {
        'login_user': user,
        'brcd_contents': chat_theme,
        'chat_contents': chat,
        'reply_contents': replies,
        'chat_id': chat_id,
        'reply_id': reply_id,
        'form': ReplyForm(),
        'img_path': chat_theme.isbn,
        'onerror': onerror, 
    }
    if request.user_agent.is_mobile:
        return render(request, 'books_mobile_HTML/reply.html', params)
    else:
        return render(request, "books_HTML/reply.html", params)
    

# Editのビュー関数   
@login_required(login_url="/") 
def edit(request, edit_id):
    # login中のuserを取り出す
    user = Account.objects.get(user=request.user)
    brcd = BookRecord.objects.get(id=edit_id)
    pre_list = [brcd.group, brcd.genre, brcd.score, brcd.summary, brcd.report]
    if brcd.owner != user:
        messages.success(request, '自分のでないレコードは編集できません。')
        return redirect(to=f'/books/chat/{brcd.id}')
    # POST送信時の処理
    if (request.method == 'POST'):
        reviced = BookRecordForm(request.POST, instance=brcd)
        group_form = GroupSelectForm(user, request.POST)
        rev_group = request.POST.get("groups")
        genre_form = GenreSelectForm(request.POST)
        rev_genre = request.POST.get("genre")
        
        if (reviced.is_valid() and group_form.is_valid() and genre_form.is_valid()):
            brcd.genre = rev_genre
            brcd.group = Group.objects.get(title=rev_group)
            brcd.save()
            reviced.save()
            post_list = [brcd.group, brcd.genre, brcd.score, brcd.summary, brcd.report]
            if post_list == pre_list: # まったく編集せずPOST!をクリックした場合
                return redirect(to=f'/books/chat/{edit_id}') # edit_dateは更新されてしまうが、edit_countは更新されない
            brcd.edit_count += 1
            brcd.save()
            return redirect(to=f'/books/chat/{edit_id}')
        
    # GETアクセス時の処理
    else:
        reviced = BookRecordForm(instance=brcd)
        genre_form = GenreSelectForm({"genre": brcd.genre})
        group_form = GroupSelectForm(user, {"groups": brcd.group.title})
    # 共通処理
    params = {
        'login_user': user,
        'id': edit_id,
        'form': reviced,
        'genre_form': genre_form,
        'group_form': group_form,
        'brcd': brcd,
    }
    if request.user_agent.is_mobile:
        return render(request, 'books_mobile_HTML/edit.html', params)
    else:
        return render(request, 'books_HTML/edit.html', params)

# Repostのビュー関数   
@login_required(login_url="/") 
def repost(request, repost_id):
    # login中のuserを取り出す
    user = Account.objects.get(user=request.user)
    brcd = BookRecord.objects.get(id=repost_id)
    if brcd.owner != user:
        messages.success(request, '自分のでないレコードはリポストできません。')
        return redirect(to=f'/books/chat/{repost_id}')
    # POST送信時の処理
    if (request.method == 'POST'):
        repost = BookRecord()
        reviced = BookRecordForm(request.POST, instance=brcd)
        group_form = GroupSelectForm(user, request.POST)
        rev_group = request.POST.get("groups")
        genre_form = GenreSelectForm(request.POST)
        rev_genre = request.POST.get("genre")
        
        if (reviced.is_valid() and group_form.is_valid() and genre_form.is_valid()):
            repost.genre = rev_genre
            repost.group = Group.objects.get(title=rev_group)
            repost.owner = user
            repost.isbn = brcd.isbn
            repost.title = brcd.title
            repost.first_author = request.POST['first_author']
            repost.img_path = brcd.img_path
            repost.pub_year = request.POST['pub_year']
            repost.score = request.POST['score']
            repost.summary = request.POST['summary']
            repost.report = request.POST['report']
            if repost.group == brcd.group:
                messages.error(request, 'もとのレコードと同じGroupが選択されています。')
                return redirect(to=f'/books/repost/{repost_id}')
            repost.save()
            messages.success(request, 'レコードをリポストしました！')
            return redirect(to='/home')
        
    # GETアクセス時の処理
    else:
        reviced = BookRecordForm(instance=brcd)
        genre_form = GenreSelectForm({"genre": brcd.genre})
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
        return render(request, 'books_mobile_HTML/repost.html', params)
    else:
        return render(request, 'books_HTML/repost.html', params)

# Deleteのビュー関数
@login_required(login_url="/")
def delete(request, del_id):
    # login中のuserを取り出す
    user = Account.objects.get(user=request.user)
    brcd = BookRecord.objects.get(id=del_id)
    if brcd.owner != user:
        messages.success(request, "自分のでないレコードは削除できません")
        return redirect(f'/books/chat/{del_id}')        
    # POST送信時の処理
    if (request.method == 'POST'):
        brcd.delete()
        chats = Chat.objects.filter(record=brcd)
        for chat in chats:
            chat.delete()
        messages.success(request, 'レコードを削除しました。')
        return redirect(to='/home')
    # GETアクセス時の処理
    # 共通処理
    params = {
        'login_user': user,
        'id': del_id,
        'contents': brcd,
    }
    if request.user_agent.is_mobile:
        return render(request, 'books_mobile_HTML/delete.html', params)
    else:
        return render(request, 'books_HTML/delete.html', params)


    
# 以降は普通の関数=====================================================================

# 指定されたグループおよびジャンルによるBookRecordの取得
def get_your_group_bookrecord(owner, glist, genlist, page):
    page_num = 8 # ページ当たりの表示数
    # publicの取得
    (public_user, public_group) = get_public()
    # チェックされたGroupの取得
    groups = Group.objects.filter(title__in=glist)
    bookrecords = BookRecord.objects.filter(group__in=groups).filter(genre__in=genlist).distinct()
    # ページネーションで指定ページを取得
    page_item = Paginator(bookrecords, page_num)
    return page_item.get_page(page)
    
# publicなUserとGroupを取得する
def get_public():
    public_user = Account.objects.filter(user__username='public').first()
    public_group = Group.objects.filter(owner=public_user).first()
    return (public_user, public_group)

# GroupメンバーのLINEに通知
def line_notification(user, group, att="post", friend=None, url="", record=""):
    members = group.member.all()
    member_lineid_list = []
    if friend==None:
        for member in members:
            token = member.user.LINE_ID
            if token != "" and token != None:
                blineid = fernet.decrypt(token)
                member_lineid_list.append(blineid.decode('utf-8'))
    else:
        token = friend.user.LINE_ID
        if token != None:
            blineid = fernet.decrypt(token)
            member_lineid_list.append(blineid.decode('utf-8'))
    if group.owner.LINE_ID != None:
        blineid = fernet.decrypt(group.owner.LINE_ID)
        member_lineid_list.append(blineid.decode('utf-8'))
    if att == "post":
        msg = "『" + str(record.title) + "』\n" + "New POST by " + str(user.user.username) + " detected!\n" + str(homepage_link) + url
    elif att == "comment":
        msg = "『" + str(record.title) + "』\n" + "New Comment by " + str(user.user.username) + " detected!\n" + str(homepage_link) + url
    elif att == "group":
        msg = "【" + str(group.title) + "】\n" + "New Member joined!\n" + str(homepage_link)
    elif att == "friend":
        msg = str(user.user.username) + " buddies up to you!\n" + str(homepage_link)
    message = create_message(msg)
    SendMsg(member_lineid_list, message)
    print("LINEで通知しました")
