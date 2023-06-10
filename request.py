import sys
import backend_lib as sql

containers = sql.init_database()

username = sys.argv[1]
passwrd = sys.argv[2]
sid = int(sys.argv[3])
p_mode = bool(int(sys.argv[4]))

stat, msg = sql.append_user(containers, username)
stat, msg, uuid = sql.append_session(containers, username, passwrd, sid, p_mode)

print(stat)
print(msg)
print(uuid)