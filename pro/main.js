#!/usr/bin/env node
 // -*- encoding: utf-8 -*-

/*
@File       :   main.js
@Time       :   2023/02/19 18:40:00
@Author     :   Mark Song
@Version    :   4.2
@Contact:   :   marksong0730@gmail.com
*/

var http = require('http');
const {
    hostname
} = require('os');
var url = require('url');
var util = require('util');
var fs = require('fs');
const {
    runInNewContext
} = require('vm');
const querystring = require('querystring')

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
    var access_ip = req.headers['cf-connecting-ip'];

    log(access_ip, "access to " + q.path, 'null');

    fn = pwd + "transactions/access"

    console.log(req.headers.host)
    if (req.headers.host !== "tsinglan.live") {
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
        fs.appendFileSync(fn, access_ip + "\t" + formatDate(new Date()) + '\t' + req.method + ' ' +req.headers['x-forwarded-proto'] + '://' + req.headers.host + q.path + '\n')
        fs.appendFileSync(fn + "minimal", access_ip + "\t" + formatDate(new Date()) + '\t' + access + '\n')
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
            if ((body.name != undefined) && (body.pass != undefined) && (body.sid != undefined) && (body.type != undefined)) {
                if (body.type == 0) {
                    const {
                        spawn
                    } = require('child_process')
                    filename = pwd + 'transactions/requests' + body.name
                    try {
                        fs.writeFileSync(filename + "{re", body.name + ' ' + body.pass + ' ' + body.sid)
                        fs.unlinkSync(filename)
                        // fs.appendFileSync(pwd+'transactions/alpha_access', access_ip+"\t"+formatDate(new Date())+"\t"+params.name+"\t"+params.sid+"\n")

                    } catch (err) {
                        console.error(err)
                    }
                    try {
                        fs.appendFileSync(pwd + 'transactions/alpha_access', access_ip + "\t" + formatDate(new Date()) + "\t" + body.name + "\t" + body.sid + '\t' + req.method + ' ' +req.headers['x-forwarded-proto'] + '://' + req.headers.host + q.path + '\n')
                    } catch (err) {
                        console.error(err)
                    }
                    log(access_ip, 'echo \"' + body.name + ' ' + body.pass + ' ' + body.sid + '\" >> ' + filename, body.name);
                    res.write("{\"rstatus\":true}");
                    const command1 = spawn('nohup python ' + pwd + 'score4.py ' + pwd + 'transactions/requests' + body.name + '{re &', {
                        shell: true
                    })
                    log(access_ip, 'nohup python ' + pwd + 'score4.py ' + pwd + 'transactions/requests' + body.name + '{re &', body.name)
                    return res.end();
                } else {

                    const {
                        spawn
                    } = require('child_process')
                    filename = pwd + 'transactions/requests' + body.name;
                    if (fs.existsSync(filename + '{re')) {
                        fs.readFile(filename + '{re', function(err, data) {
                            pass = data.toString()
                            pass = pass.substring(pass.indexOf(' ') + 1)
                            pass = pass.substring(0, pass.indexOf(' '))
                            if (pass === body.pass.toString() && fs.existsSync(filename)) {
                                fs.readFile(filename, function(err, data) {
                                    if (data.toString().startsWith('{')) {
                                        res.write(data.toString());
                                    } else {
                                        res.write("{\"rstatus\":false}");
                                    }
                                    fs.unlinkSync(filename)
                                    fs.unlinkSync(filename + '{re')
                                    log(access_ip, data, body.name);
                                    return res.end();
                                });
                            } else {
                                res.write("{\"rstatus\":false}");
                                return res.end();
                            }
                        });
                    } else {
                        res.write("{\"rstatus\":false}");
                        return res.end();
                    }
                }
            } else {
                res.write("{\"err\": true, \"status\": true}");
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
    }else if(access.startsWith("/ico/")){
        filename = pwd+"favicon.ico"
        log(access_ip,"want to read "+filename,'null')
        if(fs.existsSync(filename)){
            fs.readFile(filename, function(err, data) {
                res.writeHead(200, {'Content-Type': 'image/x-icon'});
                res.write(data);
                return res.end();
            });
        }else{
            res.writeHead(404, {'Content-Type': 'text/html'});
            return res.end("404 Not Found @ "+access);
        }
    }else if(access==="/favicon.ico"){
        filename = pwd+"ico/favicon.ico"
        log(access_ip,"want to read "+filename,'null')
        if(fs.existsSync(filename)){
            fs.readFile(filename, function(err, data) {
                res.writeHead(200, {'Content-Type': 'image/x-icon'});
                res.write(data);
                return res.end();
            });
        }else{
            res.writeHead(404, {'Content-Type': 'text/html'});
            return res.end("404 Not Found @ "+access);
        }
    }else{
        res.writeHead(404, {'Content-Type': 'text/html'});
        return res.end("404 Not Found @ "+access);
    }
}).listen(3100);