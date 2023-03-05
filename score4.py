#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File       :   score4.py
@Time       :   2023/02/20 22:23:00
@Author     :   Mark Song
@Version    :   4.0
@Contact:   :   marksong0730@gmail.com
'''

# If you want to use the present semester, then just replace semesterid with 0

import requests
import asyncio
import json
import sys
import os
import time
import aiohttp
from hashlib import md5
from math import ceil, floor


with open(sys.argv[1], 'rb') as f:
    try:  # catch OSError in case of a one line file 
        f.seek(-2, os.SEEK_END)
        while f.read(1) != b'\n':
            f.seek(-2, os.SEEK_CUR)
    except OSError:
        f.seek(0)
    ll = f.readline().decode()
ll = ll.rsplit(' ', 1)
usc = ll[0].rsplit(' ', 1)

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

stmp, enc = enc(usc[1])

# Payload when submitting the login request
payload = {
    "name": usc[0],
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
    if (per>=97 and per<=100):
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

async def main(sid):
    session = aiohttp.ClientSession('https://tsinglanstudent.schoolis.cn/')
    resp1 = await session.post('/api/MemberShip/Login', data=payload)
    aget = await get(session,'/api/School/GetSchoolSemesters')
    if not "data" in aget:
        Jdict["err"] = True
        Jdict["err_type"] = "Login Failed"
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
        done, pending = await asyncio.wait(task_list, timeout=None)
        task_ids = []
        for i in done:
            ret = i.result()
            if(ret['data']['list'][0]['finishState'] == 1):
                task_ids.append(i.result()['data']['list'][0]['id'])
        task_list = []
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
                Jdict["err_type"] = "Invalid Task Exists"
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
                Jdict["err_type"] = "Task with invaild subject"
            else:
                tasks_by_subject[subject_ids.index(tasks_info[i][0])].append(tasks_info[i])
        tasks_info = tasks_by_subject
        len_ = len(tasks_by_subject)
        for i in range(len_):
            dis = True
            gpa = get_gpa(tasks_by_subject[i])
            if("AP" in subject_names[i]) or ("A Level" in subject_names[i]) or ("Linear Algebra" in subject_names[i]) or ("AS" in subject_names[i]):
                gpa = percentage_to_weight(gpa,True)
            elif ("Physical Education" in subject_names[i]) or (is_contains_chinese(subject_names[i])) or ("PE" in subject_names[i]):
                dis = False
                gpa *= 100
            else:
                gpa = percentage_to_weight(gpa,False)
            stri = '%.1f'%gpa
            if dis:
                Jdict[subject_names[i]] = stri

print(Jdict)

loop = asyncio.get_event_loop()
loop.run_until_complete(main(int(ll[1])))

json_object = json.dumps(Jdict, indent = 4) 

print(json_object)

print("done")

f = open(sys.argv[1][:-3], "w")
f.write(json_object)
f.close()