import backend_lib as sql
import json


def fetch(uuid: str, password: str, ua: str):
    containers = sql.init_database()
    result = sql.get_session(containers, uuid)
    ua_expect = result["ua"]
    if ua_expect != ua:
        return json.loads(
            '{\n    "rstatus": true,\n    "err": true,\n    "error_en": "Unknown Error",\n    "error_zh": "\\u672a\\u77e5\\u9519\\u8bef"\n}'
        )

    err = '{\n    "rstatus": true,\n    "err": true,\n    "error_en": "Unknown Error",\n    "error_zh": "\\u672a\\u77e5\\u9519\\u8bef"\n}'

    dotyped = False
    try:
        type, fetch = sql.get_session_feedback(
            containers, uuid, password
        )
        dotyped = True
    except:
        fetch = err

    if dotyped:
        if not type:
            fetch = (
                '{\n    "rstatus": true,\n    "err": true,\n    "error_en": "'
                + fetch
                + '",\n    "error_zh": "'
                + fetch
                + '"\n}'
            )

    if len(fetch) == 0:
        fetch = '{\n    "rstatus": false\n}'

    if fetch[0] != "{":
        fetch = '{\n    "rstatus": false\n}'
    return json.loads(fetch)
