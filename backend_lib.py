import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from uuid import uuid4 as idgen
from time import sleep, time

import config

HOST = config.settings["host"]
MASTER_KEY = config.settings["master_key"]
DATABASE_PREFIX = config.settings["database_prefix"]
CONTAINER_PREFIX = config.settings["container_prefix"]
AES_KEY = "18T23ctC6udK0mSS"
MODE = config.settings["mode"]
NORMAL_LIMIT = config.settings["normal_limit"]
ONHOLD_LIMIT = config.settings["onhold_limit"]
ONHOLD_THRESHOLD = config.settings["onhold_threshold"]
SUFFIX = config.settings["suffix"]

if MODE != 'whitelist' and MODE != 'blacklist' and MODE != 'limit':
    raise Exception("MODE must be either whitelist, blacklist, or limit!")

import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher(object):
    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[: AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size :])).decode("utf-8")

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        cipher_enc = cipher.encrypt(raw.encode())
        return_text = base64.b64encode(iv + cipher_enc).decode("ascii")
        return return_text

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[: -ord(s[len(s) - 1 :])]

def encrypt(password: str):
    aes_obj = AESCipher(AES_KEY)
    return aes_obj.encrypt(password)

def decrypt(password: str):
    aes_obj = AESCipher(AES_KEY)
    return aes_obj.decrypt(password)

def gen_user_info(username: str, timeofaccess: int = 0, Cname: str = "", Ename: str = ""):
    user = {
        "id": username,
        "username": username,
        "timeOfAccess": timeofaccess,
        "Cname": Cname,
        "Ename": Ename,
    }
    return user

def gen_subject_info(subjectid: str, subjectname: str, subject_int: str, subjectname_cn: str, max_score: str):
    subject_int = str(subject_int)
    subject = {
        'id': subjectid,
        'subjectname': subject_int,
        'en': subjectname,
        'cn': subjectname_cn,
        'max_score': max_score,
    }
    
    return subject

def gen_user_permit(username: str, userRole: str = "user", timeofuse: int = 0, next_renewal: int = 0):
    user_permit = {
        "id": username,
        "username": username,
        "timeOfUse": timeofuse,
        'next_renewal': next_renewal,
        "userRole": userRole,
    }
    return user_permit

def gen_session(
    username: str,
    uuid: str,
    password: str,
    semesterID: int,
    percentage_mode: bool,
    f_state: int = 0,
    f_content:str = ''
):
    session = {
        "id": uuid,
        "uuid": uuid,
        "username": username,
        "password": password,
        "semesterID": semesterID,
        "percentage_mode": percentage_mode,
        "content": f_content,
        "feedbackState": f_state,  # 0 submitted request, -1 not permitted to run, 1 done, 2 error occur
    }
    return session

def init_database():
    DATABASE_ID = DATABASE_PREFIX + SUFFIX
    CONTAINER_ID_INFO = CONTAINER_PREFIX + SUFFIX + "_info"
    CONTAINER_ID_PERMIT = CONTAINER_PREFIX + SUFFIX + "_permit"
    CONTAINER_ID_RECORD = CONTAINER_PREFIX + SUFFIX + "_record"
    CONTAINER_ID_SUBJECT = CONTAINER_PREFIX + SUFFIX + "_subject"
    containers = []
    
    

    client = cosmos_client.CosmosClient(HOST, {"masterKey": MASTER_KEY})
    try:
        db = client.create_database(id=DATABASE_ID)

    except exceptions.CosmosResourceExistsError:
        db = client.get_database_client(DATABASE_ID)

    
    try:
        container = db.create_container(
            id=CONTAINER_ID_INFO, partition_key=PartitionKey(path="/username")
        )
    except exceptions.CosmosResourceExistsError:
        container = db.get_container_client(CONTAINER_ID_INFO)

    containers.append(container)

    try:
        container = db.create_container(
            id=CONTAINER_ID_PERMIT, partition_key=PartitionKey(path="/username")
        )
    except exceptions.CosmosResourceExistsError:
        container = db.get_container_client(CONTAINER_ID_PERMIT)

    containers.append(container)
    
    try:
        container = db.create_container(
            id=CONTAINER_ID_RECORD, partition_key=PartitionKey(path="/uuid")
        )
    except exceptions.CosmosResourceExistsError:
        container = db.get_container_client(CONTAINER_ID_RECORD)

    containers.append(container)

    try:
        container = db.create_container(
            id=CONTAINER_ID_SUBJECT, partition_key=PartitionKey(path="/subjectname")
        )
    except exceptions.CosmosResourceExistsError:
        container = db.get_container_client(CONTAINER_ID_SUBJECT)

    containers.append(container)

    return containers

def query_subject(containers, subject: str):
    
    subject = str(subject)
    
    container = containers[3]
    
    items = list(
        container.query_items(
            query="SELECT * FROM c WHERE c.subjectname=@subject",
            parameters=[{"name": "@subject", "value": subject}],
        )
    )

    return items

def query_user(containers, user: str):
    
    container = containers[0]
    
    items = list(
        container.query_items(
            query="SELECT * FROM r WHERE r.username=@user",
            parameters=[{"name": "@user", "value": user}],
        )
    )

    return items

def get_user_info(container, username: str):
    try:
        return container.read_item(item=username, partition_key=username)
    except:
        return None

def get_permit(containers: list, username: str):
    try:
        return [
            containers[1]
            .read_item(item=username, partition_key=username)
            .get("timeOfUse"),
            containers[1]
            .read_item(item=username, partition_key=username)
            .get("userRole"),
            containers[0]
            .read_item(item=username, partition_key=username)
            .get("timeOfAccess"),
            containers[0]
            .read_item(item=username, partition_key=username)
            .get("timeOfAccess")
            < containers[1]
            .read_item(item=username, partition_key=username)
            .get("timeOfUse"),
            containers[1]
            .read_item(item=username, partition_key=username)
            .get("next_renewal"),
        ]  # timeOfUse, userRole, timeOfAccess, do_permit, next_permit_time
    except:
        return None

def append_user(containers: list, username: str):
    if get_user_info(containers[0], username) is None:
        user_info = gen_user_info(username)
        containers[0].create_item(body=user_info)
        user_permit = gen_user_permit(username)
        containers[1].create_item(body=user_permit)
        update_session_count(containers, username, 0, 'change', int(time()))
        return True, "Success"
    else:
        return False, "User already exists"

def get_session(containers: list, uuid: str):
    try:
        return containers[2].read_item(item=uuid, partition_key=uuid)
    except:
        return None

def append_session(
    containers: list, username: str, password: str, sid: int, percentage_mode: bool
):
    uuid = str(idgen())
    permit_info = get_permit(containers, username)
    password = encrypt(password)
    if get_user_info(containers[0], username) is None:
        record = gen_session(username, uuid, password, sid, percentage_mode, 0)
        return False, 'User not exist', uuid
    operation_state = False
    if MODE == 'blacklist':
        if permit_info[1] == "admin":
            record = gen_session(username, uuid, password, sid, percentage_mode, 0)
            operation_state = True
        elif permit_info[1] == 'bl_user':
            operation_state = False
            record = gen_session(username, uuid, password, sid, percentage_mode, -1)
        elif permit_info[3]:
            record = gen_session(username, uuid, password, sid, percentage_mode, 0)
            operation_state = True
        elif permit_info[4] < time():
            record = gen_session(username, uuid, password, sid, percentage_mode, 0)
            operation_state = True
            new_time_of_access = permit_info[2] + (NORMAL_LIMIT if permit_info[1]=='user' else ONHOLD_LIMIT)
            new_next_renewal = int(time()) + 3600*24
            update_session_count(containers, username, new_time_of_access, 'change', new_next_renewal)
        elif permit_info[2] - ONHOLD_LIMIT > permit_info[0]:
            operation_state = False
            record = gen_session(username, uuid, password, sid, percentage_mode, -1)
            change_user_role(containers, username, 'spamCTRL')
        else:
            operation_state = False
            record = gen_session(username, uuid, password, sid, percentage_mode, -1)
        containers[2].create_item(body=record)
        return operation_state, 'Success' if operation_state else 'Not authorized to use', uuid
    elif MODE == 'whitelist':
        if permit_info[1] == "admin":
            record = gen_session(username, uuid, password, sid, percentage_mode, 0)
            operation_state = True
        elif permit_info[1] == "bl_user" or permit_info[1] == "user":
            operation_state = False
            record = gen_session(username, uuid, password, sid, percentage_mode, -1)
        elif permit_info[3]:
            record = gen_session(username, uuid, password, sid, percentage_mode, 0)
            operation_state = True
        elif permit_info[4] < time():
            record = gen_session(username, uuid, password, sid, percentage_mode, 0)
            operation_state = True
            new_time_of_access = permit_info[2] + (NORMAL_LIMIT if permit_info[1]=='wl_user' else ONHOLD_LIMIT)
            new_next_renewal = int(time()) + 3600*24
            update_session_count(containers, username, new_time_of_access, 'change', new_next_renewal)
        elif permit_info[2] - ONHOLD_LIMIT > permit_info[0]:
            operation_state = False
            record = gen_session(username, uuid, password, sid, percentage_mode, -1)
            change_user_role(containers, username, 'spamCTRL')
        else:
            operation_state = False
            record = gen_session(username, uuid, password, sid, percentage_mode, -1)
        containers[2].create_item(body=record)
        return operation_state, 'Success' if operation_state else 'Not authorized to use', uuid
    elif MODE == 'limit':
        if permit_info[1] == "admin":
            record = gen_session(username, uuid, password, sid, percentage_mode, 0)
            operation_state = True
        elif permit_info[1] == 'bl_user':
            operation_state = False
            record = gen_session(username, uuid, password, sid, percentage_mode, -1)
        elif permit_info[3]:
            record = gen_session(username, uuid, password, sid, percentage_mode, 0)
            operation_state = True
        else:
            operation_state = False
            record = gen_session(username, uuid, password, sid, percentage_mode, -1)
        containers[2].create_item(body=record)
        return operation_state, 'Success' if operation_state else 'Not authorized to use', uuid
    return False, 'Unknown error', uuid

def change_user_role(containers: list, username: str, userRole: str):
    if userRole != 'admin' and userRole != 'user' and userRole != 'wl_user' and userRole != 'spamCTRL' and userRole != 'bl_user':
        return False, 'Userrole invalid'
    if get_user_info(containers[0], username) is None:
        return False, 'User not exist'
    user_permit = get_permit(containers, username)
    if user_permit is None:
        return False, 'User information incomplete'
    user_permit = gen_user_permit(username, userRole,user_permit[0])
    containers[1].upsert_item(body=user_permit)
    return True, 'Success'

def feedback_session(
    containers: list, uuid: str, username: str, feedback_content: str
):
    try:
        data = containers[0].read_item(item=username, partition_key=username)
    except:
        return False, 'User info not found'
    user_info = gen_user_info(username,data.get('timeOfAccess')+1,data.get('Cname'),data.get('Ename'))
    containers[0].upsert_item(body=user_info)
    try:
        data = containers[2].read_item(item=uuid, partition_key=uuid)
    except:
        return False, 'Session info not found'
    session_data = gen_session(username,uuid,data.get('password'),data.get('semesterID'),data.get('percentage_mode'),1,feedback_content)
    containers[2].upsert_item(body=session_data)
    return True, 'Success'

def update_session_count(
    containers: list, username: str, timeofuse: str, operation: str = 'add', next_renewal: int = 0
):
    if operation != 'add' and operation != 'change':
        return False, 'Operation invalid'
    try:
        data = containers[1].read_item(item=username, partition_key=username)
    except:
        return False, 'User information incomplete'
    if next_renewal == 0:
        next_renewal = data.get('next_renewal')
    permit_data = gen_user_permit(username,data.get('userRole'),data.get('timeOfUse')+timeofuse if operation == 'add' else timeofuse, next_renewal)
    containers[1].upsert_item(body=permit_data)
    return True, 'Success'

def upsert(container, item):
    container.upsert_item(body=item)

def get_session_feedback(containers: list, uuid: str, password: str):
    try:
        data = containers[2].read_item(item=uuid, partition_key=uuid)
    except:
        return False, 'Session info not found'
    expect_password = decrypt(data.get('password'))
    if expect_password != password:
        return False, 'Password incorrect'
    return True, data.get('content')

def run():
    containers = init_database()
    append_user(containers,'marksong')
    change_user_role(containers,'marksong','user')
    update_session_count(containers,'marksong',2,'change')
    do_run, _, uuid = append_session(containers,'marksong','passwordofmarksong',0,False)
    print('done')
    sleep(10)
    if do_run:
        feedback_session(containers,uuid,'marksong','helloworld1')
    
    do_run, _, uuid = append_session(containers,'marksong','passwordofmarksong',0,False)
    if do_run:
        feedback_session(containers,uuid,'marksong','helloworld2')
    do_run, _, uuid = append_session(containers,'marksong','passwordofmarksong',0,False)
    if do_run:
        feedback_session(containers,uuid,'marksong','helloworld3')
    do_run, _, uuid = append_session(containers,'marksong','passwordofmarksong',0,False)
    if do_run:
        feedback_session(containers,uuid,'marksong','helloworld4')

if __name__ == "__main__":
    run()
