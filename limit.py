import config
import sys
import sqlite3 as sql

path_to_db = config.get("database")

conn = sql.connect(path_to_db)

db = conn.cursor()

username = sys.argv[1]
operation = sys.argv[2]
number = int(sys.argv[3])

code_exec = """SELECT TIME FROM PERMIT WHERE USERNAME='"""+username+"\'"
db.execute(code_exec)
__data = db.fetchall()
if(operation == '+'):
    if(not len(__data)==0):
        number += __data[0][0]
if(len(__data)==0):
    code_exec = """INSERT INTO PERMIT (USERNAME, TIME) VALUES ('"""+username+"""',"""+str(number)+""");"""
else:
    code_exec = """UPDATE PERMIT SET TIME="""+str(number)+""" WHERE USERNAME='"""+username+"\'"
print(code_exec)
db.execute(code_exec)

conn.commit()
conn.close()
