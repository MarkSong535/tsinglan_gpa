#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File       :   db_init.py
@Time       :   2023/03/11
@Author     :   Mark Song
@Version    :   7.0
@Contact:   :   marksong0730@gmail.com
'''

from os.path import exists
import sqlite3 as sql
import config

path_to_db = config.get("database")

n_db_exist = False if exists(path_to_db) else True

if n_db_exist:
    conn = sql.connect(path_to_db) 
    db = conn.cursor()
    db.execute(
        """CREATE TABLE USER (
            ID INTEGER PRIMARY KEY, 
            USERNAME TEXT NOT NULL, 
            SESSION_COUNT INT NOT NULL, 
            PERMIT_TYPE INT DEFAULT 0);"""
    )
    db.execute(
        """CREATE TABLE SESSION (
            S_ID INTEGER PRIMARY KEY,
            U_ID INT NOT NULL,
            TIMESTAMP INT NOT NULL,
            USERNAME TEXT NOT NULL,
            PASSWORD TEXT NOT NULL, 
            SEMESTER INT NOT NULL,
            STATUS INT NOT NULL,
            SPEC INT NOT NULL,
            RETURN_DATA TEXT,
            TIMEOUT BOOLEAN DEFAULT false);"""
    )
    conn.commit()
    conn.close()