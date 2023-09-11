import json
import backend_lib as sql


def call(username: str, password: str, sid: int, p_mode: bool, ua: str):
    containers = sql.init_database()

    stat, msg = sql.append_user(containers, username)
    stat, msg, uuid = sql.append_session(
        containers, username, password, sid, p_mode, ua
    )
    if not stat:
        Jdict = {}
        Jdict["err"] = True
        Jdict["error_en"] = msg
        Jdict["error_zh"] = msg
        json_object = json.dumps(Jdict, indent=4)
        sql.feedback_session(containers, uuid, username, str(json_object), True)

    return uuid
