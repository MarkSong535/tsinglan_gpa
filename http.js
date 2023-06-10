#!/usr/bin/env node
// -*- encoding: utf-8 -*-

/*
@File       :   main.js
@Time       :   2023/03/11
@Author     :   Mark Song
@Version    :   7.0
@Contact:   :   marksong0730@gmail.com
*/

const fs = require('fs');
const config_data = JSON.parse(fs.readFileSync("config.json", 'utf8'))
const python = config_data["python"];
const port = config_data["port"];
const pwd = config_data["Father directory"];
const hostname = config_data["hostname"];
var http = require('http');
var url = require('url');
const path = require('path')
const exec = require("child_process").exec;
const querystring = require('querystring')

function padTo2Digits(num) {
    return num.toString().padStart(2, '0');
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

http.createServer(function (req, res) {
    var q = url.parse(req.url, true)
    var params = q.query;
    var access = q.pathname;
    //var access_file = q.
    var access_ip = "10.10.10.10";

    const ip_addr = req.socket.remoteAddress;

    console.log(ip_addr)

    log(access_ip, "access to " + q.path, 'null');


    fn = pwd + "transactions/access"


    /*if(req.headers.host !== hostname){
        filename = pwd + "jump.html"
        log(access_ip, "want to read " + filename, 'null')
        if (fs.existsSync(filename)) {
            fs.readFile(filename, function (err, data) {
                res.writeHead(200, {
                    'Content-Type': 'text/html'
                });
                //body = querystring.parse(body)
            });
        }
        return
    }*/

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
            if ((body.name != undefined) && (body.pass != undefined) && (body.session_id != undefined) && (body.sid != undefined) && (body.type != undefined) && (body.percentage != undefined)) {
                if ((body.type == 0)) {
                    console.log(0)

                    var cmd = python+' ' + pwd + 'request.py \"' + body.name + '\" \"' + body.pass + '\" ' + body.sid + ' ' + ((body.percentage) ? 1 : 0);
                    
                    exec(cmd,
                    function (error, stdout, stderr) {
                        console.log('stdout: ' + stdout);
                        console.log('stderr: ' + stderr);
                        if (error !== null) {
                            console.log('exec error: ' + error);
                        }else{
                            ret = stdout.split('\n');
                            if(ret[0]!="True"){
                                res.write("{\n    \"rstatus\": false,\n    \"err\": true,\n    \"message\": \""+ret[1]+"r\",\n    \"error_zh\": \""+ret[1]+"\"\n}");
                                res.end();
                            }else{
                                res.write("{\"rstatus\":true,\"session_id\":\"" + ret[2] + "\"}");
                                module.exports = function myTest() {
    
                                    return new Promise(function (resolve, reject) {
            
                                        var cmd = python+' ' + pwd + 'manipulate.py \"' + ret[2] + "\"";
                                        
                                        exec(cmd, {
                                            maxBuffer: 1024 * 2000
                                        }, function (err, stdout, stderr) {
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
                                return res.end();

                            }
                        }
                    });
                } else if ((body.type == 1)) {
                    var cmd = python+' ' + pwd + 'fetch.py \"' + body.session_id + '\" \"' + body.pass + '\"';
                    exec(cmd,
                        function (error, stdout, stderr) {
                            console.log('stdout: ' + stdout);
                            console.log('stderr: ' + stderr);
                            console.log('this ')
                            if (error !== null) {
                                console.log('exec error: ' + error);
                            }else{
                                ret = stdout
                                console.log('ret')
                                console.log(ret)
                                res.write(ret)
                                return res.end();
                            }
                        });
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
            fs.readFile(filename, function (err, data) {
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
    } else if (access === "/en/") {

        access = access.substring(1);
        filename = pwd + "index_en.html"
        log(access_ip, "want to read " + filename, 'null')
        if (fs.existsSync(filename)) {
            fs.readFile(filename, function (err, data) {
                res.writeHead(200, {
                    'Content-Type': 'text/html'
                });
                res.write(data);
                return res.end();
            });
        }
    } else if (access === "/data.json") {

        access = access.substring(1);
        filename = pwd + "data.json"
        log(access_ip, "want to read " + filename, 'null')
        if (fs.existsSync(filename)) {
            fs.readFile(filename, function (err, data) {
                res.writeHead(200, {
                    'Content-Type': 'text/json',
                    'charset': 'utf-8'
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
            fs.readFile(filename, function (err, data) {
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
            fs.readFile(filename, function (err, data) {
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
    } else if (access === "/assets/bootstrap/css/bootstrap.min.css"){
        filename = pwd+"html_assets/"+path.basename(access)
        log(access_ip, "want to read " + filename, 'null')
        fs.readFile(filename, function (err, data) {
            res.writeHead(200, {
                'Content-Type': 'text/css'
            });
            res.write(data);
            return res.end();
        });
    } else if (access === "/assets/css/styles.css"){
        filename = pwd+"html_assets/"+path.basename(access)
        log(access_ip, "want to read " + filename, 'null')
        fs.readFile(filename, function (err, data) {
            res.writeHead(200, {
                'Content-Type': 'text/css'
            });
            res.write(data);
            return res.end();
        });
    } else if (access === "/assets/bootstrap/js/bootstrap.min.js"){
        filename = pwd+"html_assets/"+path.basename(access)
        log(access_ip, "want to read " + filename, 'null')
        fs.readFile(filename, function (err, data) {
            res.writeHead(200, {
                'Content-Type': 'text/javascript'
            });
            res.write(data);
            return res.end();
        });
    } else if (access === "/assets/js/jquery.min.js"){
        filename = pwd+"html_assets/"+path.basename(access)
        log(access_ip, "want to read " + filename, 'null')
        fs.readFile(filename, function (err, data) {
            res.writeHead(200, {
                'Content-Type': 'text/javascript'
            });
            res.write(data);
            return res.end();
        });
    } else if (access === "/assets/css/Login-Form-Basic-icons.css"){
        filename = pwd+"html_assets/"+path.basename(access)
        log(access_ip, "want to read " + filename, 'null')
        fs.readFile(filename, function (err, data) {
            res.writeHead(200, {
                'Content-Type': 'text/css'
            });
            res.write(data);
            return res.end();
        });
    } else if (fs.existsSync(pwd + "ico/" + path.basename(access))) {
        filename = pwd + "ico/" + path.basename(access)
        log(access_ip, "want to read " + filename, 'null')
        fs.readFile(filename, function (err, data) {
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
}).listen(port);