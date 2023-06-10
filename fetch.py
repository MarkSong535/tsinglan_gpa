import backend_lib as sql
import sys

containters = sql.init_database()

err = "{\n    \"rstatus\": true,\n    \"err\": true,\n    \"error_en\": \"Unknown Error\",\n    \"error_zh\": \"\\u672a\\u77e5\\u9519\\u8bef\"\n}"

dotyped = False
try:
    type, fetch = sql.get_session_feedback(containters, sys.argv[1], sys.argv[2])#uuid, password
    dotyped = True
except:
    fetch = err

if dotyped:
    if not type:
        fetch = "{\n    \"rstatus\": true,\n    \"err\": true,\n    \"error_en\": \""+fetch+"\",\n    \"error_zh\": \""+fetch+"\"\n}"

if len(fetch)==0:
    fetch = "{\n    \"rstatus\": false\n}"
    
if fetch[0]!="{":
    fetch = "{\n    \"rstatus\": false\n}"

print(fetch)