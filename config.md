# How to config `config.json`

## Father directory

the directory where `score.py` is located (including `\` at the end of the directory)

## ipinfo_key

Key for ipinfo to aquire ip geographic information (for spam protection)

## mode

There are three modes available:

- blacklist: everyone except the blacklisted (id is 3) can access and onhold user can use with further limited amount per day.

- whitelist: only the whitelisted (id is 1 & 9) can access and authorized user (id is 1) can access with limited amount of time.

- limit: user can only use assigned amount of times (except for admin (id = 9)).

## database

The path for the database file, it should be Father directory + `database\db.db`

## normal_user_daily_limit

The number of time that a default user can use per day (in whitelist mode).

## onhold_user_daily_limit

The number of time that an onhold user can use per day

## onhold_threshold

The number of time that any user except admin can use before to be put onhold.

## hostname

The hostname of the server, for spam protection.

## port

The port that node should listen to.

## miao_key

The key for miao to send notification.