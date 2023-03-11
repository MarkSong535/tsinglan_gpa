from os.path import exists
import sqlite3 as sql
import sys
import time
import config

def velocity(session_id):
    path_to_db = config.get("database")
    conn = sql.connect(path_to_db)
    db = conn.cursor()
    _time = int(time.time()*1000)
    code_exec = """SELECT U_ID FROM SESSION WHERE S_ID="""+session_id
    db.execute(code_exec)
    u_id = db.fetchall()[0][0]
    code_exec = """SELECT * FROM SESSION WHERE U_ID="""+str(u_id)+""" AND TIMEOUT=false"""
    db.execute(code_exec)
    fetched = db.fetchall()
    count = 0
    for i in fetched:
        time_difference = _time - i[2]
        if(time_difference>86400000):
        #if(time_difference>60000):
            code_exec = """UPDATE SESSION SET TIMEOUT=true WHERE S_ID="""+str(i[0])
        else:
            count += 1
    conn.commit()
    conn.close
    return count

