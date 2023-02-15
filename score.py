#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File       :   score.py
@Time       :   2023/02/15 20:14:30
@Author     :   Mark Song
@Coauthor   :   Bruno Chen
@Version    :   1.1
@Contact:   :   marksong0730@gmail.com
'''

# Set your password to !Hello!*1 , then run python score.py name semesterid
# If you want to use the present semester, then just replace semesterid with 0
# !Hello!*1
import requests
import json
import sys
from math import ceil, floor

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

Jdict = dict()

Jdict["err"] = False
### Begin user define

# Payload when submitting the login request
payload = {
    "name": sys.argv[1],
    "password": "BD0B42120E634BCEAB4485AFB64991AA",
    "timestamp": 1676457462,
    "isWeekPassword": 0,
    "LanguageType": 1
}


### End user define

sid_ = int(sys.argv[2])

def get_grade_list_url(sub, page, sid):
    if sid_ != 0:
        sid = int(sys.argv[2])
    start, end = semesterId_to_time(sid)
    return 'https://tsinglanstudent.schoolis.cn/api/LearningTask/GetList?semesterId='+str(sid)+'&subjectId='+sub+'&typeId=null&key=&beginTime='+start+'&endTime='+end+'&pageIndex='+str(page)+'&pageSize=1'

def get_task_info(task_id):
    return 'https://tsinglanstudent.schoolis.cn/api/LearningTask/GetDetail?learningTaskId='+str(task_id)

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

# Use 'with' to ensure the session context is closed after use.
with requests.Session() as s:
    # Login
    p = s.post('https://tsinglanstudent.schoolis.cn/api/MemberShip/Login', data=payload)
    if json.loads(p.text)['data']:# If login result return true
        Jdict["status"] = True
        sid = s.get('https://tsinglanstudent.schoolis.cn/api/School/GetSchoolSemesters')
        sid = int(json.loads(sid.text)['data'][0]['id'])
        r = s.get(get_grade_list_url('null',1,sid))
        count = json.loads(r.text)['data']['totalCount']
        indices = []

        # get task ids
        task_ids = []
        task_ids_failed = []
        for i in range(count):
            task_num = i
            if(task_num<count):
                raw = s.get(get_grade_list_url('null',i+1,sid))
                indices.append(json.loads(raw.text))
                if json.loads(raw.text)['data']['list'][0]['finishState'] == 1:
                    task_ids.append(json.loads(raw.text)['data']['list'][0]['id'])
                else:
                    task_ids_failed.append(json.loads(raw.text)['data']['list'][0]['id'])
        
        # get subject list
        subs = []
        subs_p = []
        w_grade = []
        sum_proportion = []
        max_len = 0
        for i in task_ids:
            raw = s.get(get_task_info(i))
            if (json.loads(raw.text)['data']==None):
                Jdict["err"] = True
            sub = str(json.loads(raw.text)['data']['subjectId'])
            state = str(json.loads(raw.text)['data']['isInSubjectScore'])
            finish = json.loads(raw.text)['data']['finishState']
            if not sub in subs:
                subs.append(sub) 
                subs_p.append(json.loads(raw.text)['data']['subjectName'])
            if finish == 1 and json.loads(raw.text)['data']['isInSubjectScore'] and json.loads(raw.text)['data']['score']!=None:
                port_len = len(json.loads(raw.text)['data']['evaProjects'])
                ports = []
                for i in json.loads(raw.text)['data']['evaProjects']:
                    ports.append([i['id'],i['proportion']])
                tasks_info.append([sub,json.loads(raw.text)['data']['evaProjects'][1]['id'],json.loads(raw.text)['data']['score'],json.loads(raw.text)['data']['totalScore'],ports])
        
        tasks_by_subject = []
        for _ in subs:
            tasks_by_subject.append([])
        number_tasks = len(tasks_info)
        for i in range(number_tasks):
            if not tasks_info[i][0] in subs:
                Jdict["err"] = True
            else:
                tasks_by_subject[subs.index(tasks_info[i][0])].append(tasks_info[i])
        tasks_info = tasks_by_subject
        len_ = len(tasks_by_subject)
        for i in range(len_):
            dis = True
            gpa = get_gpa(tasks_by_subject[i])
            if("AP" in subs_p[i]) or ("A Level" in subs_p[i]) or ("Linear Algebra" in subs_p[i]):
                gpa = percentage_to_weight(gpa,True)
            elif ("Physical Education" in subs_p[i]) or (is_contains_chinese(subs_p[i])) or ("PE" in subs_p[i]):
                dis = False
                gpa *= 100
            else:
                gpa = percentage_to_weight(gpa,False)
            stri = '%.1f'%gpa
            if dis:
                Jdict[subs_p[i]] = stri
    else:
        Jdict["status"] = False

json_object = json.dumps(Jdict, indent = 4) 

print(json_object)
