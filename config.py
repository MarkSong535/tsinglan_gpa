#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File       :   config.py
@Time       :   2023/03/11
@Author     :   Mark Song
@Version    :   7.0
@Contact:   :   marksong0730@gmail.com
'''
import json
import os

path = os.path.dirname(os.path.abspath(__file__))+"/config.json"

data = ""

with open(path,'r',encoding='utf-8') as json_file:
    data = json.load(json_file)

def get(config):
    return data[config]