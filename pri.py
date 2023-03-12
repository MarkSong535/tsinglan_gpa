import config
import sqlite3 as sql

path_to_db = config.get("database")

conn = sql.connect(path_to_db)

db = conn.cursor()

db.execute("""SELECT * FROM USER WHERE SESSION_COUNT!=0 ORDER BY SESSION_COUNT DESC""")

data = db.fetchall()

print("""<meta charset="utf-8">""")
print("""<h1>获取记录</h1>""")
print("""<table border="1" cellspacing="0"><thead><tr><th>中文姓名</th><th>英文姓名</th><th>登录名</th><th>成功/总请求数量</th><th>请求成功率</th><th>用户类型</th></tr></thead>""")

start = "<tr><td align=center>"
inter = "</td><td align=center>"
end = "</td></tr>"
for i in data:
    uid = i[0]
    db.execute("""SELECT COUNT(*) FROM SESSION WHERE U_ID="""+str(uid))
    data_ = db.fetchall()[0][0]
    per = '%.1f'%(int(i[2]*100)/data_)+'%'
    print(start,i[4],inter,i[5],inter,i[1],inter,i[2],'/',data_,inter,per,inter,i[3],end)

print('<tr></tr>')

db.execute("""SELECT * FROM USER WHERE SESSION_COUNT=0""")

data = db.fetchall()

for i in data:
    uid = i[0]
    db.execute("""SELECT COUNT(*) FROM SESSION WHERE U_ID="""+str(uid))
    data_ = db.fetchall()[0][0]
    per = '%.1f'%(int(i[2]*100)/data_)+'%'
    print(start,i[4],inter,i[5],inter,i[1],inter,i[2],'/',data_,inter,per,end)

print("""</table>""")
print("""<h1>科目列表</h1>""")
print("""<table border="1" cellspacing="0"><thead><tr><th>科目代号</th><th>科目名称（英文）</th><th>科目名称（中文）</th><th>GPA占比</th></tr></thead>""")

db.execute("""SELECT * FROM SUBJECT ORDER BY SUB_KEY ASC""")
data = db.fetchall()

for i in data:
    print(start,i[1],inter,i[2],inter,i[3],inter,i[6],end)

print("""</table>""")

conn.close()