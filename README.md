# GPA Fetcher Official REPO (BitBucket)

[Official Site](https://gpa_tls.marksong.tech)

[Official Paid Site](https://paid_tls.marksong.tech)

[Site Admin Email](mailto:tls@marksong.tech)

[Docker Repo](https://hub.docker.com/r/markilibrium535/tsinglan-school-gpa)

[Docker code repo](https://bitbucket.org/markstech1/gpa_fetcher_docker/)

[Notes to Official Site Maintainer](https://bitbucket.org/markstech1/gpa_fetcher_w-password)

<p align="center">
  <a href="./LICENSE">
    <img src="https://img.shields.io/badge/license-GNU%20AGPLv3-blue"/>
  </a>
</p>

## Instruction

### Install Prerequisites

python (with pip) is required for this project.

`pip install -r requirements.txt`

### Run

`uvicorn main:app --host 0.0.0.0 --port 80` (set the port to the port you would like to use)

## Database Structure

### *_info

This is the place where user info are stored.

- id

    Xiaobao username (key identifier)

- username

    Xiaobao username

- timeOfAccess

    Time that the requests that the user had made

- Cname

    Chinese name of the user (fetched from Xiaobao)

- Ename

    English name of the user (fetched from Xiaobao)

### *_permit

This is the place where user permit are stored.

There are five kinds of user: admin, user, wl_user, spamCTRL, bl_user.

Admin can make access to the site without any regulation.

Bl_user (blacklist user) cannot make any access to the site.

Wl_user (whitelist user) can make access to the site in whitelist mode.

SpamCTRL (spam control) can make access to the site in blacklist mode with limited amount of access time.

User can make access to the site in blacklist mode.

- id

    Xiaobao username (key identifier)

- username

    Xiaobao username

- timeOfUse

    Times that the user are permited to use before next permit renewal

- next_renewal

    Time that the user are permited make permit renewal

- userRole

    User role (admin, user, wl_user, spamCTRL, bl_user)

### *_record

This is the place that each request made are stored.

- id

    ID of the request (uuid4) (key identifier)

- uuid

    UUID of the request (uuid4)

- username

    Xiaobao username

- password

    Xiaobao password (encrypted using AES)

- semesterID

    Semester that is being requested

- percentage_mode

    Percentage mode (1/0)

- content

    Content of the request

- feedbackState

    The state of processing (0 not started, 1 finished, -1 denied to process)

- ua

    The user-agent of the user

### *_subject

This is the place where subject info are stored.

- id

    Five letter ID of the subject (key identifier)

- subjectname

    Xiaobao issued ID of the subject

- en

    Name of the subject (fetched from Xiaobao)

- cn

    Name of the subject in Chinese (should be translated manually)

### *_semester

This is the place where semester info are stored.

- id

    uuid of the access where this info is collected from (key identifier)

- uuid

    uuid of the access where this info is collected from

- str

    semester info

## Configurations

### `config.py`

- `host`

    The hostname of the database server (You can find it on your Azure portal)

- `master_key`

    The master key of the database server (You can find it on your Azure portal)

- `database_prefix`

    The prefix of the database that you would like to set to

- `container_prefix`

    The prefix of the containers that you would like to set to

- `mode`

    The mode you would like the server to be (`limit` have to be paid to use, `blacklist` everyone allowed to use, `whitelist`, only permited users are allowed to use)

- `onhold_threshold`

    The number of requests that the server can hold before it to be put onhold

- `normal_limit`

    The number of requests that an user can make a day

- `onhold_limit`

    The number of requests that an onhold user can make a day

- `suffix`

    The suffix of the database and containers (The name structure of the database and containers are `database_prefix` + `suffix` and `container_prefix` + `suffix` + container name)

- `enc_key`

    The key for AES encryption of passwords.

- `server_host`

    The hostname of the server (spam protection)

## Update semester info

Fetech semester info from Xiaobao [https://tsinglanstudent.schoolis.cn/api/School/GetSchoolSemesters](https://tsinglanstudent.schoolis.cn/api/School/GetSchoolSemesters), a collection of semester info can also be found in `semester` container.

Convert to JSON by running `python raw_to_data.py`

## Resources Used

[Markdown Labels](https://github.com/Mqxx/GitHub-Markdown)

[Azure Database and management SDK](https://azure.microsoft.com)

[GNU logo](https://img.shields.io/)

## Contributors

[@Mark Song](https://marksong.tech) the owner of this repository, middleware, and backend developer.

[@Bruno Chen](https://github.com/BChen233) Frontend Developer.

[@Neyoki](https://github.com/NeyokiCat) Maintainaner of code and functionality of the official site.