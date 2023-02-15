#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File       :   score.py
@Time       :   2023/02/15 13:50:00
@Author     :   Mark Song
@Version    :   1.0
@Contact:   :   marksong0730@gmail.com
'''

import requests
import json
import math

### Begin user define


# Payload when submitting the login request
payload = {
    "name": "aaaaaaa",
    "password": "aaaaaa",
    "timestamp": aaaaaa,
    "isWeekPassword": 0,
    "LanguageType": 1
}

# Uncomment the following to fetch the grade of 2022-2023 second semester
semesterId = "21208"
beginTime = "2023-01-27"
endTime = "2023-08-26"

# Uncomment the following to fetch the grade of 2021-2022 first semester
 #semesterId = "21207"
# beginTime = "2022-08-29"
# endTime = "2023-01-26"

### End user define

def get_grade_list_url(sub, page):
    return 'https://tsinglanstudent.schoolis.cn/api/LearningTask/GetList?semesterId='+semesterId+'&subjectId='+sub+'&typeId=null&key=&beginTime='+beginTime+'&endTime='+endTime+'&pageIndex='+str(page)+'&pageSize=1'

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

tasks_info = []

# Use 'with' to ensure the session context is closed after use.
with requests.Session() as s:
    # Login
    p = s.post('https://tsinglanstudent.schoolis.cn/api/MemberShip/Login', data=payload)
    if json.loads(p.text)['data']:# If login result return true
        r = s.get(get_grade_list_url('null',1))
        count = json.loads(r.text)['data']['totalCount']

        indices = []


        # get task ids
        task_ids = []
        task_ids_failed = []
        for i in range(count):
            task_num = i
            if(task_num<count):
                raw = s.get(get_grade_list_url('null',i+1))
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
                print("error")
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
                print("invalid subject id")
            else:
                tasks_by_subject[subs.index(tasks_info[i][0])].append(tasks_info[i])
        tasks_info = tasks_by_subject
        len_ = len(tasks_by_subject)
        for i in range(len_):
                stri = '%.1f'%get_gpa(tasks_by_subject[i])
                print(subs_p[i]+' : '+stri) 
    else:
        print('login failed')