# Tsinglan GPA Calculator

<p align="center">
  <a href="./LICENSE">
    <img src="https://img.shields.io/badge/license-GNU%20AGPLv3-blue"/>
  </a>
</p>

## Calculate your gpa by yourself

### [Init](config.md)

Write the `config.json` file according to `config.json.templete`

### Install Prerequisits

Requires nodejs, npm, python, pip

`pip install requirements.txt`

`npm install -g pm2`

`npm install node-ipinfo`

### Start Backend

`python db_paid_init.py`

`pm2 start http.js`

### Add Blacklist Username

Add the username into a newline of `total_bl`

### Add Whitelist Username

Add the username into a newline of `total_wl`

### Assign User Role

In table `USER`, 9 is admin, 1 is user with access in whitelist mode, 0 is default user, 2 is user onhold (due to frequent access), 3 is blocked user.

### Add/Change Times that the users can Use (in `limit` mode)

`python limit.py + 1` add 1 additional time the user can use

`python limit.py x 1` change to a single time the user can use

### Sync school semester data

Download [`GetSchoolSemesters`](https://tsinglanstudent.schoolis.cn/api/School/GetSchoolSemesters) from schoolis and put it into the same directory as `score.py`.

Run `python raw_to_data.py`

## Contributors:

[@Mark Song](https://marksong.tech) the owner of this repository, middleware and backend developer.

[@Bruno Chen](https://github.com/BChen233) Frontend Developer

[@Neyoki](https://github.com/NeyokiCat) Maintainance of code



