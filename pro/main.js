#!/usr/bin/env node
// -*- encoding: utf-8 -*-

/*
@File       :   main.js
@Time       :   2023/02/16 22:46:00
@Author     :   Mark Song
@Version    :   3.0
@Contact:   :   marksong0730@gmail.com
*/

var http = require('http');
const { hostname } = require('os');
var url = require('url');
var util = require('util');
var fs = require('fs');
const { runInNewContext } = require('vm');

const pwd = __dirname.substr(0, __dirname.length-3);

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

function log(ip, msg){
    console.log(ip+" "+formatDate(new Date())+" "+msg)
}

http.createServer(function(req, res) {
    var q = url.parse(req.url, true)
    var params = q.query;
    var access = q.pathname;
    var access_ip = req.headers['cf-connecting-ip'];

    log(access_ip,"access to "+q.path);
    if(access.startsWith("/fet/") || access==="/fet"){
        res.writeHead(200, {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        });
        if ((!params) || (!params.name) || (!params.sid)) {
            res.write("{\"err\": true, \"status\": true}");
            res.end();
            log(access_ip,"lack of info");
        } else {
            if(!params.type){
                log(access_ip,'python3 '+pwd+'score.py ' + params.name + ' ' + params.sid)
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
                        log(access_ip,data_string);
                    } else {
                        res.write("{\"err\": true, \"status\": true}");
                        log(access_ip,"bad python");
                    }
                    res.end();
                });
            }else{
                filename = pwd+'transactions/requests'+params.name;
                if(params.type==0){
                    if ((!params.pass)){
                        const {
                            spawn
                        } = require('child_process')
                        
                        try{
                            fs.writeFileSync(filename, params.name + ' ' + params.sid)
                        } catch (err){
                            console.error(err)
                        }
                        log(access_ip,'echo \"' + params.name + ' ' + params.sid+'\" >> '+filename);
                        res.write("{\"rstatus\":true}");
                        const command1 = spawn('nohup python3 '+pwd+'score2.py '+pwd+'transactions/requests'+params.name+' &', {
                            shell: true
                        })
                        log(access_ip,'nohup python3 '+pwd+'score2.py '+pwd+'transactions/requests'+params.name+' &')
                        return res.end();
                    }else{
                        const {
                            spawn
                        } = require('child_process')
                        
                        try{
                            fs.writeFileSync(filename, params.name + ' ' + params.pass + ' ' + params.sid)
                        } catch (err){
                            console.error(err)
                        }
                        log(access_ip,'echo \"' + params.name + ' ' + params.pass + ' ' + params.sid+'\" >> '+filename);
                        res.write("{\"rstatus\":true}");
                        const command1 = spawn('nohup python3 '+pwd+'score3.py '+pwd+'transactions/requests'+params.name+' &', {
                            shell: true
                        })
                        log(access_ip,'nohup python3 '+pwd+'score3.py '+pwd+'transactions/requests'+params.name+' &')
                        return res.end();
                    }
                }else if(params.type==1){
                    const {
                        spawn
                    } = require('child_process')
                    filename = pwd+'transactions/requests'+params.name;
                    if(fs.existsSync(filename)){
                        fs.readFile(filename, function(err, data) {
                            if(data.toString().startsWith('{')){
                                res.write(data.toString());
                            }else{
                                res.write("{\"rstatus\":false}");
                            }
                            log(access_ip, data);
                            return res.end();
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
    }else if(access==="/"){
        filename = pwd+"index.html"
        log(access_ip,"want to read "+filename)
        if(fs.existsSync(filename)){
            fs.readFile(filename, function(err, data) {
                res.writeHead(200, {'Content-Type': 'text/html'});
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