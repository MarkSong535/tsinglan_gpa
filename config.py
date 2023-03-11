import json
import os

path = os.path.dirname(os.path.abspath(__file__))+"/config.json"

data = ""

with open(path,'r',encoding='utf-8') as json_file:
    data = json.load(json_file)

def get(config):
    return data[config]