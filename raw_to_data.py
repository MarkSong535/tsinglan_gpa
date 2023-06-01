import json
import config

f = open(config.get("Father directory")+'GetSchoolSemesters','r')

data = json.load(f)

def to_text(year, semester):
    year = int(year)
    return str(year) + '-' + str(year+1) + ' 第' + str(semester) + '学期', str(year) + '-' + str(year+1) + ' ' + ('First Semester' if semester == 1 else 'Second Semester')

dict_zh = []

dict_en = []


dict_zh_temp = {}
dict_zh_temp["text"] = '当前学期'
dict_zh_temp["value"] = 0
dict_en_temp = {}
dict_en_temp["text"] = 'Current Semester'
dict_en_temp["value"] = 0
dict_zh.append(dict_zh_temp)
dict_en.append(dict_en_temp)

for i in data['data']:
    dict_z, dict_e = to_text(i['year'], i['semester'])
    dict_zh_temp = {}
    dict_zh_temp["text"] = dict_z
    dict_zh_temp["value"] = i['id']
    dict_en_temp = {}
    dict_en_temp["text"] = dict_e
    dict_en_temp["value"] = i['id']
    dict_zh.append(dict_zh_temp)
    dict_en.append(dict_en_temp)

dict = {"en":dict_en,"zh":dict_zh}
json_object = json.dumps(dict, indent = 4)

with open(config.get("Father directory")+"data.json", "w") as outfile:
    json.dump(dict, outfile, indent=4)