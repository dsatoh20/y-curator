"""
kanso = "ポメラニアンのつむじが好き。"
selected = "つむじ"

kanso_splited = kanso.split(selected)

kanso_highlighted = kanso_splited[0] + "<a href='#'><mark>" + selected + "</mark></a>" + kanso_splited[1]

print(kanso_highlighted)

# selectedが複数含まれるとき、一つ目として扱う
kanso = "ポメラニアンのつむじが好き。つむじが。"
selected = "つむじ"

kanso_splited = kanso.split(selected)

kanso_highlighted = kanso_splited[0] + "<a href='#'><mark>" + selected + "</mark></a>" + kanso_splited[1]

for i in range(2, len(kanso_splited)):
    kanso_highlighted += selected + kanso_splited[i]

print(kanso_highlighted)
"""
# highlightした文字列の前後にhtmlタグを挿入する
def insert_tag(highlight_id, chat_theme, highlight, reply_id, app): # 対象のbookrecordのid、ユーザーがカーソルで選択した文字列、replyページのid
    report = " " + chat_theme.report
    report_splited = report.split(highlight)
    if len(report_splited) > 1:
        report_tagged = report_splited[0] + f"<a href='/{app}/chat/{highlight_id}/reply/{reply_id}'><u>" + highlight + "</u></a>" + report_splited[1]
        
        for i in range(2, len(report_splited)):
            report_tagged += highlight + report_splited[i]
        chat_theme.report = report_tagged[1:]
        chat_theme.save()
    else:
        print('reportに該当する文字列なし')