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
const { hostname } = require('os');
var url = require('url');
var util = require('util');
var fs = require('fs');
const { runInNewContext } = require('vm');

const pwd = __dirname;

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

function log(ip, msg,name){
    console.log(ip+" "+formatDate(new Date())+" "+msg);
}

http.createServer(function(req, res) {
    var q = url.parse(req.url, true)
    var params = q.query;
    var access = q.pathname;
    var access_ip = req.headers['cf-connecting-ip'];
    
    log(access_ip,"access to "+q.path, 'null');

    fn = pwd+"transactions/access"

    try{
        fs.appendFileSync(fn+"minimal",access_ip+"\t"+formatDate(new Date())+'\t'+access+'\n')
    } catch (err){
        console.error(err)
    }

    if(access.startsWith("/fet/") || access==="/fet"){
        res.writeHead(200, {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        });
        if ((!params) || (!params.name) || (!params.sid) || (!params.pass)) {
            res.write("{\"err\": true, \"status\": true}");
            res.end();
            log(access_ip,"lack of info",'null');
        } else {
            if(!params.type){
                log(access_ip,'python3 '+pwd+'score.py ' + params.name + ' ' + params.sid,params.name)
                const {
                    spawn
                } = require('child_process')
    
                const command = spawn('python3 '+pwd+'score.py ' + params.name + ' ' + params.sid, {
                    shell: true
                })
    
                command.stdout.on('data', data => {
                    data_string = data.toString();
                    if (data_string.charAt(0) == '{') {
                        res.write(data_string);
                        data_string +=
                            params.name + ' ' + params.sid + ' ';
                        log(access_ip,data_string,params.name);
                    } else {
                        res.write("{\"err\": true, \"status\": true}");
                        log(access_ip,"bad python",params.name);
                    }
                    res.end();
                });
            }else{
                filename = pwd+'transactions/requests'+params.name;
                if(params.type==0){
                    const {
                        spawn
                    } = require('child_process')
                    
                    try{
                        fs.writeFileSync(filename+"{re", params.name + ' ' + params.pass + ' ' + params.sid)
                        fs.writeFileSync(filename,'')
                    } catch (err){
                        console.error(err)
                    }

                    log(access_ip,'echo \"' + params.name + ' ' + params.pass + ' ' + params.sid+'\" >> '+filename,params.name);
                    res.write("{\"rstatus\":true}");
                    const command1 = spawn('nohup python '+pwd+'score4.py '+pwd+'transactions/requests'+params.name+'{re &', {
                        shell: true
                    })
                    log(access_ip,'nohup python '+pwd+'score4.py '+pwd+'transactions/requests'+params.name+'{re &',params.name)
                    return res.end();
                    
                }else if(params.type==1){
                    const {
                        spawn
                    } = require('child_process')
                    filename = pwd+'transactions/requests'+params.name;
                    if(fs.existsSync(filename+'{re')){
                        fs.readFile(filename+'{re',function(err,data){
                            pass = data.toString()
                            pass = pass.substring(pass.indexOf(' ')+1)
                            pass = pass.substring(0,pass.indexOf(' '))
                            if(pass === params.pass.toString() && fs.existsSync(filename)){
                                fs.readFile(filename, function(err, data) {
                                    if(data.toString().startsWith('{')){
                                        res.write(data.toString());
                                    }else{
                                        res.write("{\"rstatus\":false}");
                                    }
                                    log(access_ip, data,params.name);
                                    return res.end();
                                });
                            }else{
                                res.write("{\"rstatus\":false}");
                                return res.end();
                            }
                        });
                    }else{
                        res.write("{\"rstatus\":false}");
                        return res.end();
                    }
                }else{
                    res.write("{\"rstatus\":false}");
                    return res.end();
                }
                
            }
        }
    }else if (access === "/") {
        res.writeHead(301, {'Location': '/zh/'});
        console.log(res._header);
        res.end();
    }else if (access === "/zh/") {
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