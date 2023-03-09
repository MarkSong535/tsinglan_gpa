#!/usr/bin/env node
 // -*- encoding: utf-8 -*-

/*
@File       :   main.js
@Time       :   2023/03/05 19:14:00
@Author     :   Mark Song
@Version    :   4.3
@Contact:   :   marksong0730@gmail.com
*/

var http = require('http');
const {
    hostname
} = require('os');
var url = require('url');
var util = require('util');
var fs = require('fs');
const path = require('path')
const {
    runInNewContext
} = require('vm');
const querystring = require('querystring')
const { IPinfoWrapper, LruCache } = require("node-ipinfo");

const cacheOptions = {
    max: 5000,
    maxAge: 24 * 1000 * 60 * 60,
};
const cache = new LruCache(cacheOptions);
const ipinfo = new IPinfoWrapper("", cache);

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
            if ((body.name != undefined) && (body.pass != undefined) && (body.timestamp != undefined) && (body.sid != undefined) && (body.type != undefined)) {
                if ((body.type == 0) && (!(body.spec != undefined))){
                    var timestamp = String(new Date().getTime());
                    const {
                        spawn
                    } = require('child_process')
                    const exec = require("child_process").exec;
                    filename = pwd + 'transactions/requests' + timestamp
                    try {
                        fs.writeFileSync(filename + "_cr", body.name + '\n' + body.pass + '\n' + body.sid)
                        fs.unlinkSync(filename)
                        // fs.appendFileSync(pwd+'transactions/alpha_access', access_ip+"\t"+formatDate(new Date())+"\t"+params.name+"\t"+params.sid+"\n")

                    } catch (err) {
                        console.error(err)
                    }
                    try {
                        ipinfo.lookupIp(access_ip).then((response) => {
                            fs.appendFileSync(pwd + 'transactions/alpha_access', access_ip + "\t" + response['country'] + "\t" + formatDate(new Date()) + "\t" + body.name + "\t" + body.sid + "\n")
                        });
                    } catch (err) {
                        console.error(err)
                    }
                    log(access_ip, 'echo \"' + body.name + ' ' + body.pass + ' ' + body.sid + '\" >> ' + filename, body.name);
                    //console.log('nohup python ' + pwd + 'score5.py ' + filename + '_cr &')
                    res.write("{\"rstatus\":true,\"timestamp\":\""+timestamp+"\"}");
                    //const command1 = spawn('nohup python ' + pwd + 'score5.py ' + filename + '_cr &', {
                    //    shell: true
                    //})
                    module.exports = function myTest() {
 
                        return new Promise(function(resolve, reject) {
                     
                            var cmd = 'python ' + pwd + 'score5.py ' + filename + '_cr';
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
                    return res.end();
                } else if (body.type == 0) {
                    var timestamp = String(new Date().getTime());
                    const {
                        spawn
                    } = require('child_process')
                    const exec = require("child_process").exec;
                    filename = pwd + 'transactions/requests' + timestamp
                    try {
                        fs.writeFileSync(filename + "_cr", body.name + '\n' + body.pass + '\n' + body.sid)
                        fs.unlinkSync(filename)
                        // fs.appendFileSync(pwd+'transactions/alpha_access', access_ip+"\t"+formatDate(new Date())+"\t"+params.name+"\t"+params.sid+"\n")

                    } catch (err) {
                        console.error(err)
                    }
                    try {
                        ipinfo.lookupIp(access_ip).then((response) => {
                            fs.appendFileSync(pwd + 'transactions/alpha_access', access_ip + "\t" + response['country'] + "\t" + formatDate(new Date()) + "\t" + body.name + "\t" + body.sid + "\n")
                        });
                    } catch (err) {
                        console.error(err)
                    }
                    log(access_ip, 'echo \"' + body.name + ' ' + body.pass + ' ' + body.sid + '\" >> ' + filename, body.name);
                    //console.log('nohup python ' + pwd + 'score5.py ' + filename + '_cr &')
                    res.write("{\"rstatus\":true,\"timestamp\":\""+timestamp+"\"}");
                    //const command1 = spawn('nohup python ' + pwd + 'score5.py ' + filename + '_cr &', {
                    //    shell: true
                    //})
                    module.exports = function myTest() {
 
                        return new Promise(function(resolve, reject) {
                     
                            var cmd = 'python ' + pwd + 'score6.py ' + filename + '_cr';
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
                    return res.end();
                }else {

                    const {
                        spawn
                    } = require('child_process')
                    filename = pwd + 'transactions/requests' + body.timestamp;
                    console.log(filename)
                    if (fs.existsSync(filename + '_cr')) {
                        fs.readFile(filename + '_cr', function(err, data) {
                            pass = data.toString()
                            pass = pass.substring(pass.indexOf('\n') + 1)
                            pass = pass.substring(0, pass.indexOf('\n'))
                            console.log(pass)
                            if (pass === body.pass.toString() && fs.existsSync(filename)) {
                                fs.readFile(filename, function(err, data) {
                                    if (data.toString().startsWith('{')) {
                                        res.write(data.toString());
                                    } else {
                                        res.write("{\"rstatus\":false}");
                                    }
                                    fs.unlinkSync(filename)
                                    fs.unlinkSync(filename + '_cr')
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