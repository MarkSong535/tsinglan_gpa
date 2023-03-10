#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File       :   score.py
@Time       :   2023/03/11
@Author     :   Mark Song
@Version    :   7.0
@Contact:   :   marksong0730@gmail.com
'''

import requests
import asyncio
import json
import sys
import os
import time
import aiohttp
from hashlib import md5
from math import ceil, floor
from os.path import exists
import sqlite3 as sql
from typing import List
import request_velocity
import config

mode = config.get("mode")
normal_user_max_access_per_day = config.get("normal_user_daily_limit")
hold_user_max_access_per_day = config.get("onhold_user_daily_limit")
onhold_threshold = config.get("onhold_threshold")
u_access = 0


path_to_db = config.get("database")

conn = sql.connect(path_to_db)


db = conn.cursor()

session_id = sys.argv[1]
velocity = request_velocity.velocity(session_id)
code_exec = """SELECT U_ID FROM SESSION WHERE S_ID="""+session_id
db.execute(code_exec)
u_id = db.fetchall()[0][0]
code_exec = """SELECT PERMIT_TYPE FROM USER WHERE ID="""+str(u_id)
db.execute(code_exec)
user_permit = db.fetchall()[0][0]
do_run = False
if mode == "whitelist":
    if (user_permit == 1) or (user_permit == 9):
        do_run = True
elif mode == "blacklist":
    if (user_permit == 1) or (user_permit == 9):
        do_run = True
    elif (user_permit == 2):
        if velocity <= hold_user_max_access_per_day:
            do_run = True
        u_access = hold_user_max_access_per_day
    elif (user_permit == 0):
        if velocity <= normal_user_max_access_per_day:
            do_run = True
        u_access = normal_user_max_access_per_day
if user_permit != 9 and velocity > onhold_threshold:
    code_exec = """UPDATE USER SET PERMIT_TYPE=2 WHERE ID="""+str(uid)
    db.execute(code_exec)
    conn.commit()

if do_run:
    def find_user(username: str, database: str) -> List:
        code_exec = """SELECT * FROM """+database+""" WHERE USERNAME='"""+username+"""';"""
        db.execute(code_exec)
        result = db.fetchall()
        return result

    def user_data_id(data: List) -> int:
        if len(data) == 0:
            return 0
        else:
            return data[0][0]

    def append_entry(username: str, count: int=1):
        uid = user_data_id(find_user(username, "USER"))
        code_exec = """SELECT SESSION_COUNT FROM USER WHERE ID="""+str(uid)+""";"""
        db.execute(code_exec)
        count = db.fetchall()[0][0] + count
        code_exec = """UPDATE USER SET SESSION_COUNT="""+str(count)+""" WHERE ID="""+str(uid)
        db.execute(code_exec)
        conn.commit()

    def get_db_info(se_id):
        code_exec = """SELECT * FROM SESSION WHERE S_ID="""+se_id
        db.execute(code_exec)
        return db.fetchall()[0]

    db_info = get_db_info(session_id)

    code_exec = """UPDATE SESSION SET STATUS=2 WHERE S_ID="""+str(session_id)
    db.execute(code_exec)
    conn.commit()

    def semesterId_to_time(sid):
        is_first = ((sid%2)==1)
        year = sid - 21207
        year /= 2
        year = floor(year)
        year += 2022
        start = ""
        end = ""
        if(is_first):
            start = str(year)+'-08-29'
            end = str(year+1)+'-01-26'
        else:
            start = str(year+1)+'-01-27'
            end = str(year+1)+'-08-26'
        return start, end


    def enc(pas):
        stmp = int(time.time())
        enc = md5((str(md5(pas.encode()).hexdigest()).upper()+str(stmp)).encode()).hexdigest().upper()
        return stmp, enc

    Jdict = dict()
    Jdict["rstatus"] = True
    Jdict["err"] = False

    stmp, enc = enc(db_info[4])

    # Payload when submitting the login request
    payload = {
        "name": db_info[3],
        "password": enc,
        "timestamp": stmp,
        "isWeekPassword": 0,
        "LanguageType": 1
    }


    ### End user define



    def get_grade_list_url(sub, page, sid):
        start, end = semesterId_to_time(sid)
        return '/api/LearningTask/GetList?semesterId='+str(sid)+'&subjectId='+sub+'&typeId=null&key=&beginTime='+start+'&endTime='+end+'&pageIndex='+str(page)+'&pageSize=1'

    def get_task_info(task_id):
        return '/api/LearningTask/GetDetail?learningTaskId='+str(task_id)

    def transpose(array):
        trans = []
        for _ in range(len(array[0])):
            trans.append([])
        for i in range(len(array)):
            for j in range(len(array)):
                trans[j].append(array[i][j])
        return trans

    def deepen(array):
        taged = []
        tags = []
        tag_weight = []
        for i in array:
            tag = i[2]
            if not tag in tags:
                tags.append(tag)
                taged.append([])
                tag_weight.append(i[4])
            rm_tag = i[:2]+i[3:]
            taged[tags.index(tag)].append(rm_tag)
        return taged, tag_weight

    def get_weight_table(array):
        weight_table = []
        for quater in array:
            quater_weight = []
            for types in quater:
                quater_weight.append(types[0][2]*types[0][3]/10000)
            weight_table.append(quater_weight)
        return weight_table

    def norm_weight(array, weight):
        quaters = len(array)
        for i in range(quaters):
            temp = sum(array[i])
            len_ = len(array[i])
            for j in range(len_):
                
                array[i][j] *= weight[i]/100
                array[i][j] /= temp
        temp = sum(weight[:quaters])/100
        for i in range(quaters):
            for j in range(len_):
                array[i][j] /= temp
        return array

    def sum_grade(array, weight):
        grade = 0
        len_q = len(array)
        for i in range(len_q):
            len_t = len(array[i])
            for j in range(len_t):
                tasks_grade = 0
                len_e = len(array[i][j])
                for k in range(len_e):
                    tasks_grade += array[i][j][k][0]/array[i][j][k][1]
                tasks_grade /= len_e
                tasks_grade *= weight[i][j]
                grade += tasks_grade
        return grade

    def rectanglize(array):
        max_len = 0
        for i in array:
            max_len = max(len(i),max_len)
        len_ = len(array)
        for i in range(len_):
            for _ in range(max_len - len(array[i])):
                array[i].append(0)
        return array

    def get_gpa(task_arr):
        len_ = len(task_arr)
        for i in range(len_):
            task_arr[i] = task_arr[i][2:4]+[transpose(task_arr[i][4])[0][1],transpose(task_arr[i][4])[0][0]]+[transpose(task_arr[i][4])[1][1],transpose(task_arr[i][4])[1][0]]
        structured, w = deepen(task_arr)
        deep_structured = []
        for i in structured:
            temp, _ = deepen(i)
            deep_structured.append(temp)
        weight_table = get_weight_table(deep_structured)
        weight_table = rectanglize(weight_table)
        weight_table = norm_weight(weight_table, w)
        #********
        return sum_grade(deep_structured, weight_table)*100

    def is_contains_chinese(strs):
        for _char in strs:
            if '\u4e00' <= _char <= '\u9fa5':
                return True
        return False

    def percentage_to_weight(per,state):
        score = 0
        if (per>=97):
            score = 4.3
        elif (per>=93 and per<97):
            score = 4.0
        elif (per>=90 and per<93):
            score = 3.7
        elif (per>=87 and per<90):
            score = 3.3
        elif (per>=83 and per<87):
            score = 3.0
        elif (per>=80 and per<83):
            score = 2.7
        elif (per>=77 and per<80):
            score = 2.3
        elif (per>=73 and per<77):
            score = 2.0
        elif (per>=70 and per<73):
            score = 1.7
        elif (per>=67 and per<70):
            score = 1.3
        elif (per>=63 and per<67):
            score = 1.0
        elif (per>=60 and per<63):
            score = 0.7
        else:
            score = 0
        if state:
            score += 1
            if score == 1:
                score = 0
        return score

    def percentage_to_mark(per):
        score = ''
        if (per>=97 and per<=100):
            score = 'A+'
        elif (per>=93 and per<97):
            score = 'A'
        elif (per>=90 and per<93):
            score = 'A-'
        elif (per>=87 and per<90):
            score = 'B+'
        elif (per>=83 and per<87):
            score = 'B'
        elif (per>=80 and per<83):
            score = 'B-'
        elif (per>=77 and per<80):
            score = 'C+'
        elif (per>=73 and per<77):
            score = 'C'
        elif (per>=70 and per<73):
            score = 'C-'
        elif (per>=67 and per<70):
            score = 'D+'
        elif (per>=63 and per<67):
            score = 'D'
        elif (per>=60 and per<63):
            score = 'D-'
        else:
            score = 'Failed'
        return score

    tasks_info = []

    async def get_aw(session, url):
        async with session.get(url) as resp:
            return await resp.text()

    async def get(session, url):
        async with session.get(url) as resp:
            return await resp.json()
    
    @asyncio.coroutine
    def fetch(session, url):
        with aiohttp.Timeout(10):
            resp = yield from session.get(url)
            return (yield from resp.text())
    
    async def append_subject(session,sid):
        cname = (await get(session, "/api/MemberShip/GetCurrentStudentInfo"))['data']['cName']
        ename = (await get(session, "/api/MemberShip/GetCurrentStudentInfo"))['data']['eName']
        code_exec = """UPDATE USER SET CNAME='"""+cname+"""' WHERE ID="""+str(u_id)
        db.execute(code_exec)
        conn.commit()
        code_exec = """UPDATE USER SET ENAME='"""+ename+"""' WHERE ID="""+str(u_id)
        db.execute(code_exec)
        conn.commit()
        resp = await get(session, "/api/LearningTask/GetStuSubjectListForSelect?semesterId="+str(sid))
        #resp = await resp.text()
        for i in resp['data']:
            db.execute("""SELECT * FROM SUBJECT WHERE SUB_KEY='"""+i['subjectCode']+'\'')
            data = db.fetchall()
            if(len(data)==0):
                s_name = i['name']
                weight = ''
                if("AP" in s_name) or ("A Level" in s_name) or ("Linear Algebra" in s_name) or ("AS" in s_name):
                    weight = '5.3'
                elif ("Physical Education" in s_name) or (is_contains_chinese(s_name)) or ("PE" in s_name):
                    weight = '0.0'
                else:
                    weight = '4.3'
                db.execute("""INSERT INTO SUBJECT (SUB_KEY,ENG_NAME_LIST,ENG_NAME,MAX_SCORE) VALUES('"""+i['subjectCode']+"""','"""+i['name']+"""','"""+i['name']+"""',"""+weight+""")""")
            else:
                pre_list = data[0][2]
                pre_list_split = pre_list.split(',')
                if (not i['name'] in pre_list_split):
                    pre_list += ','+i['name']
                db.execute("""UPDATE SUBJECT SET ENG_NAME_LIST='"""+pre_list+"""' WHERE SUB_KEY='"""+i['subjectCode']+'\'')
                conn.commit()

    async def main(sid):
        session = aiohttp.ClientSession('https://tsinglanstudent.schoolis.cn/')
        resp1 = await session.post('/api/MemberShip/Login', data=payload)
        aget = await get(session,'/api/School/GetSchoolSemesters')
        if not "data" in aget:
            Jdict["err"] = True
            Jdict["error_en"] = "Schoolis Login Failed"
            Jdict["error_zh"] = "??????????????????"
            return
        if(sid == 0):
            sid = aget['data'][0]['id']
        async with session.get(get_grade_list_url('null',1,sid)) as req:
            js = await req.json()
            count = js['data']['totalCount']
            task_list = []
            for i in range(count):
                task = asyncio.create_task(get(session,get_grade_list_url('null',i+1,sid)))
                task_list.append(task)
            if len(task_list) == 0:
                return
            done, pending = await asyncio.wait(task_list, timeout=None)
            task_ids = []
            for i in done:
                ret = i.result()
                if(ret['data']['list'][0]['finishState'] == 1):
                    task_ids.append(i.result()['data']['list'][0]['id'])
            task_list = []
            await append_subject(session,sid)
            for i in task_ids:
                task = asyncio.create_task(get(session,get_task_info(i)))
                task_list.append(task)
            done, pending = await asyncio.wait(task_list, timeout=None)
            subject_ids = []
            subject_names = []
            tasks_info = []
            for i in done:
                ret = i.result()
                if (ret['data']==None):
                    Jdict["err"] = True
                    Jdict["error_en"] = "Invalid Task Exists"
                    Jdict["error_zh"] = "??????????????????"
                sub = str(ret['data']['subjectId'])
                state = str(ret['data']['isInSubjectScore'])
                finish = ret['data']['finishState']
                if not sub in subject_ids:
                    subject_ids.append(sub) 
                    subject_names.append(ret['data']['subjectName'])
                if finish == 1 and ret['data']['isInSubjectScore'] and ret['data']['score']!=None:
                    port_len = len(ret['data']['evaProjects'])
                    ports = []
                    for j in ret['data']['evaProjects']:
                        ports.append([j['id'],j['proportion']])
                    tasks_info.append([sub,ret['data']['evaProjects'][1]['id'],ret['data']['score'],ret['data']['totalScore'],ports])
            tasks_by_subject = []
            for _ in subject_ids:
                tasks_by_subject.append([])
            number_tasks = len(tasks_info)
            for i in range(number_tasks):
                if not tasks_info[i][0] in subject_ids:
                    Jdict["err"] = True
                    Jdict["error_en"] = "Task with invaild subject"
                    Jdict["error_zh"] = "??????????????????"
                else:
                    tasks_by_subject[subject_ids.index(tasks_info[i][0])].append(tasks_info[i])
            tasks_info = tasks_by_subject
            len_ = len(tasks_by_subject)
            __len = len_
            total_grade = 0
            for i in range(len_):
                dis = True
                gpa = get_gpa(tasks_by_subject[i])
                db.execute("""SELECT * FROM SUBJECT WHERE ENG_NAME_LIST LIKE '%"""+subject_names[i]+"""%'""")
                if db_info[7] == 1:
                    stri = '%.1f'%gpa
                    stri += " "+percentage_to_mark(gpa)
                    __temp_ = db.fetchall()[0][6]
                    if __temp_ != 0:
                        total_grade += gpa
                    else:
                        __len -= 1
                    Jdict[subject_names[i]] = stri
                else:
                    __temp_ = db.fetchall()[0][6]
                    __temp = percentage_to_weight(float('%.1f'%gpa),(__temp_==5.3))
                    if __temp_ == 0:
                        __temp = 0
                        __len -= 1
                    stri = '%.1f'%__temp
                    stri += " "+percentage_to_mark(gpa)
                    if dis:
                        total_grade += __temp
                    Jdict[subject_names[i]] = stri
            if db_info[7] == 1:
                Jdict["Total GPA"] = '%.1f'%(total_grade/__len)+' N/A'
            else:
                Jdict["Total GPA"] = '%.2f'%(total_grade/__len)+' N/A'
        await session.close()
        

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(int(db_info[5])))
    if(len(Jdict.keys())==2):
        Jdict["err"] = True
        Jdict["error_en"] = "None Schoolis Entry Found"
        Jdict["error_zh"] = "??????????????????????????????"
    json_object = json.dumps(Jdict, indent = 4) 

    if not Jdict["err"]:
        append_entry(db_info[3])

    try:
        i = sys.argv[2]
        append_entry(db_info[3],int(sys.argv[2]))
        print(json_object)
    except:
        print()

    code_exec = """UPDATE SESSION SET RETURN_DATA='"""+str(json_object)+"""' WHERE S_ID="""+str(session_id)
    db.execute(code_exec)
    conn.commit()
    code_exec = """UPDATE SESSION SET STATUS=1 WHERE S_ID="""+str(session_id)
    db.execute(code_exec)
    conn.commit()
    db.execute("""SELECT * FROM SESSION WHERE S_ID="""+str(session_id))
    conn.close()
else:
    code_exec = """UPDATE SESSION SET RETURN_DATA='{"rstatus":true,"error_en":"You
     have exceeded the number of request you can make today.You can only make
     """+str(u_access)+""" request in a 24 hour interval."""+("""Your account is onhold
     due to spam protection, contact website admin to remove your onhold status.""" if
       user_permit == 2 else "")+"""","error_zh":"???????????????????????????????????????24??????????????????
       """+str(u_access)+"""????????????"""+("""????????????????????????????????????????????????????????????????????????????????????
       ???????????????????????????????????????""" if user_permit == 2 else "")+""""}' WHERE S_ID="""+str(session_id)
    code_exec = code_exec.replace('\n', '').replace('    ', '').replace('   ', '').replace('  ', '')
    db.execute(code_exec)
    conn.commit()
    code_exec = """UPDATE SESSION SET STATUS=1 WHERE S_ID="""+str(session_id)
    db.execute(code_exec)
    conn.commit()
    conn.close()