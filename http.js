#!/usr/bin/env node
 // -*- encoding: utf-8 -*-

/*
@File       :   main.js
@Time       :   2023/03/05 19:14:00
@Author     :   Mark Song
@Version    :   4.3
@Contact:   :   marksong0730@gmail.com
*/

const fs = require('fs');
const db_file = '/Users/marksong/Project/tsinglan_gpa/database/db_test1.db';
const hostname = ''
const ipinfo_key = ""
const sqlite3 = require('sqlite3');
var http = require('http');
var url = require('url');
const path = require('path')
const exec = require("child_process").exec;
const querystring = require('querystring')
const { IPinfoWrapper, LruCache } = require("node-ipinfo");
var db = new sqlite3.Database(db_file);

async function get_id(username){
    return new Promise(function(resolve, reject) {
        db.all("SELECT * FROM USER WHERE USERNAME=\'"+username+"\'",function(err,row){
            js = JSON.stringify(row)
            if(row.toString()==""){
                db.prepare("INSERT INTO USER (USERNAME, SESSION_COUNT) VALUES (\'"+username+"\',0);").run()
                resolve(get_id(username))
            }else{
                resolve(row[0]['ID'])
            }
        });
    });
}

async function push_data(username, password, semester, spec) {
    //"""INSERT INTO SESSION (U_ID, TIMESTAMP, PASSWORD, SEMESTER, STATUS) VALUES (0,100,'HW',0,0);"""
    var id=await get_id(username);
    var code = "INSERT INTO SESSION (U_ID, TIMESTAMP, USERNAME, PASSWORD, SEMESTER, STATUS, SPEC) VALUES ("+String(id)+","+String(Date.now())+",\'"+username+"\',\'"+password+"\',"+semester+",0,"+String(spec)+");"
    db.prepare(code).run()
    console.log(code)
}
const cacheOptions = {
    max: 5000,
    maxAge: 24 * 1000 * 60 * 60,
};
const cache = new LruCache(cacheOptions);
const ipinfo = new IPinfoWrapper(ipinfo_key, cache);

const pwd = __dirname.substr(0, __dirname.length - 3);

function padTo2Digits(num) {
    return num.toString().padStart(2, '0');
}

function print(i) {
    console.log(i)
}

function formatDate(date) {
    return (
        [
            date.getFullYear(),
            padTo2Digits(date.getMonth() + 1),
            padTo2Digits(date.getDate()),
        ].join('-') +
        ' ' + [
            padTo2Digits(date.getHours()),
            padTo2Digits(date.getMinutes()),
            padTo2Digits(date.getSeconds()),
        ].join(':')
    );
}

function log(ip, msg, name) {
    console.log(ip + " " + formatDate(new Date()) + " " + msg);
}

http.createServer(function(req, res) {
    var q = url.parse(req.url, true)
    var params = q.query;
    var access = q.pathname;
    //var access_file = q.
    var access_ip = req.headers['cf-connecting-ip'];

    log(access_ip, "access to " + q.path, 'null');


    fn = pwd + "transactions/access"

    console.log(req.headers.host)
    if (req.headers.host !== hostname) {
        filename = pwd + "jump.html"
        log(access_ip, "want to read " + filename, 'null')
        if (fs.existsSync(filename)) {
            fs.readFile(filename, function(err, data) {
                res.writeHead(200, {
                    'Content-Type': 'text/html'
                });
                res.write(data);
                return res.end();
            });
        }
    }

    try {
        ipinfo.lookupIp(access_ip).then((response) => {
            fs.appendFileSync(fn, access_ip + "\t" + response['country'] + "\t" + formatDate(new Date()) + '\t' + req.headers['x-forwarded-proto'] + '://' + req.headers.host + q.path + '\n')
            fs.appendFileSync(fn + "minimal", access_ip + "\t" + response['country'] + "\t" + formatDate(new Date()) + '\t' + access + '\n')
        });
    } catch (err) {
        console.error(err)
    }

    if (req.method === 'POST') {
        let body = '';

        // very important to handle errors
        req.on('error', (err) => {
            if (err) {
                response.writeHead(500, {
                    'Content-Type': 'text/html'
                });
                response.write('An error occurred');
                response.end();
            }
        });

        // read chunks of POST data
        req.on('data', chunk => {
            body += chunk.toString();
        });

        // when complete POST data is received
        req.on('end', () => {
            // use parse() method
            if (body.indexOf("{") >= 0) {
                body = JSON.parse(body)
            } else {
                body = querystring.parse(body)
            }
            if ((body.name != undefined) && (body.pass != undefined) && (body.session_id != undefined) && (body.sid != undefined) && (body.type != undefined)) {
                if ((body.type == 0)){
                    push_data(body.name, body.pass, body.sid, ((body.spec != undefined)?1:0))
                    .then(() => db.all("SELECT * FROM SESSION WHERE USERNAME=\'"+body.name+"\' order by S_ID desc limit 1",function(err,row){
                        //console.log(row[0]['S_ID'])
                        try {
                            ipinfo.lookupIp(access_ip).then((response) => {
                                fs.appendFileSync(pwd + 'transactions/alpha_access', access_ip + "\t" + response['country'] + "\t" + formatDate(new Date()) + "\t" + body.name + "\t" + body.sid + "\n")
                            });
                        } catch (err) {
                            console.error(err)
                        }
                        console.log(body.spec)
                        module.exports = function myTest() {
 
                            return new Promise(function(resolve, reject) {
                         
                                var cmd = 'python ' + pwd + 'score7.py ' + row[0]['S_ID'];
                                console.log(cmd)
                                log(access_ip,cmd)
                                exec(cmd,{
                                    maxBuffer: 1024 * 2000
                                }, function(err, stdout, stderr) {
                                    if (err) {
                                        console.log(err);
                                        reject(err);
                                    } else if (stderr.lenght > 0) {
                                        reject(new Error(stderr.toString()));
                                    } else {
                                        console.log(stdout);
                                        resolve();
                                    }
                                });
                            });
                        };
                        module.exports()
                        res.write("{\"rstatus\":true,\"session_id\":\""+row[0]['S_ID']+"\"}");
                        return res.end();
                    }))
                } else if ((body.type == 1)){
                    db.all("SELECT * FROM SESSION WHERE USERNAME=\'"+body.name+"\' AND S_ID="+body.session_id+" AND PASSWORD=\'"+body.pass+"\'",function(err,row){
                        try{
                            if(row[0]['STATUS']===1){
                                res.write(row[0]['RETURN_DATA']);
                                console.log(row[0]['RETURN_DATA'])
                            }else{
                                res.write("{\"rstatus\":false}");
                            }
                        }catch{
                            res.write("{\"rstatus\":true,\"session_id\":\"err\"}");
                        }
                        return res.end();
                    })
                } else {
                    res.write("{\"rstatus\":false}");
                    return res.end();
                }
            } else {
                res.write("{\"err\": true, \"status\": true}");
                console.log(body)
                res.end();
                log(access_ip, "lack of info", 'null');
            }


            // rest of the code
        });
    } else if (access === "/") {
        res.writeHead(301, {
            'Location': '/zh/'
        });
        console.log(res._header);
        res.end();
    } else if (access === "/zh/") {
        access = access.substring(1);
        filename = pwd + "index.html"
        log(access_ip, "want to read " + filename, 'null')
        if (fs.existsSync(filename)) {
            fs.readFile(filename, function(err, data) {
                res.writeHead(200, {
                    'Content-Type': 'text/html'
                });
                res.write(data);
                return res.end();
            });
        } else {
            res.writeHead(404, {
                'Content-Type': 'text/html'
            });
            return res.end("404 Not Found @ " + access);
        }
    } else if (access === "/zh/spec/") {

        access = access.substring(1);
        filename = pwd + "index_spec.html"
        log(access_ip, "want to read " + filename, 'null')
        if (fs.existsSync(filename)) {
            fs.readFile(filename, function(err, data) {
                res.writeHead(200, {
                    'Content-Type': 'text/html'
                });
                res.write(data);
                return res.end();
            });
        }
    } else if (access === "/en/") {

        access = access.substring(1);
        filename = pwd + "index_en.html"
        log(access_ip, "want to read " + filename, 'null')
        if (fs.existsSync(filename)) {
            fs.readFile(filename, function(err, data) {
                res.writeHead(200, {
                    'Content-Type': 'text/html'
                });
                res.write(data);
                return res.end();
            });
        }
    } else if (access === "/en/spec/") {

        access = access.substring(1);
        filename = pwd + "index_spec_en.html"
        log(access_ip, "want to read " + filename, 'null')
        if (fs.existsSync(filename)) {
            fs.readFile(filename, function(err, data) {
                res.writeHead(200, {
                    'Content-Type': 'text/html'
                });
                res.write(data);
                return res.end();
            });
        }
    } else if (access === "/terms.html") {

        access = access.substring(1);
        filename = pwd + "tc.html"
        log(access_ip, "want to read " + filename, 'null')
        if (fs.existsSync(filename)) {
            fs.readFile(filename, function(err, data) {
                res.writeHead(200, {
                    'Content-Type': 'text/html'
                });
                res.write(data);
                return res.end();
            });
        }
    } else if (access === "/favicon.ico") {
        filename = pwd + "ico/favicon.ico"
        log(access_ip, "want to read " + filename, 'null')
        if (fs.existsSync(filename)) {
            fs.readFile(filename, function(err, data) {
                res.writeHead(200, {
                    'Content-Type': 'image/x-icon'
                });
                res.write(data);
                return res.end();
            });
        } else {
            res.writeHead(404, {
                'Content-Type': 'text/html'
            });
            return res.end("404 Not Found @ " + access);
        }
    } else if (fs.existsSync(pwd+"ico/"+path.basename(access))) {
        filename = pwd+"ico/"+path.basename(access)
        log(access_ip, "want to read " + filename, 'null')
        fs.readFile(filename, function(err, data) {
            res.writeHead(200, {
                'Content-Type': 'image/x-icon'
            });
            res.write(data);
            return res.end();
        });
    } else {
        res.writeHead(404, {
            'Content-Type': 'text/html'
        });
        return res.end("404 Not Found @ " + access);
    }
}).listen(3100);