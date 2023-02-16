var http = require('http');
const { hostname } = require('os');
var url = require('url');
var util = require('util');
var fs = require('fs');
const { runInNewContext } = require('vm');

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
                log(access_ip,'python3 /Users/marksong/Project/tsinglan_gpa/score.py ' + params.name + ' ' + params.sid)
                const {
                    spawn
                } = require('child_process')
    
                const command = spawn('python3 /Users/marksong/Project/tsinglan_gpa/score.py ' + params.name + ' ' + params.sid, {
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
                if(params.type==0){
                    const {
                        spawn
                    } = require('child_process')
        
                    const command = spawn('echo \"' + params.name + ' ' + params.sid+'\" >> /Users/marksong/Project/tsinglan_gpa/transactions/requests', {
                        shell: true
                    })
                    log(access_ip,'echo \"' + params.name + ' ' + params.sid+'\" >> /Users/marksong/Project/tsinglan_gpa/transactions/requests')
                    // command.stdout.on('data', data => {
                    //     console.log(formatDate(new Date())+" safe");
                    //     res.write("{'rstatus':true}");
                
                    //     res.end();
                    // });
                    command.stderr.on('data', data =>{
                        res.write("{\'rstatus\':true}");
                        res.end();
                        log(access_ip,"error while writing");
                    });
                }else if(params.type==1){
                    res.write("fetch to proxy");
                }else{
                    res.write("{'rstatus':false}");
                }
                res.end();
            }
        }
    }else if(access.startsWith("/prt/") || access==="/prt"){
        res.writeHead(200, {
            'Content-Type': 'application/html',
            'Access-Control-Allow-Origin': '*'
        });
        request_url = access;
        if(access==="/prt"){
            access+="/"
        }
        if(access==="/prt/"){
            access+="index.html"
        }
        filename = access.slice(5);
        filename = "/Users/marksong/Project/tsinglan_gpa/html_assests/" + filename;
        log(access_ip,"want to read "+filename)
        if(fs.existsSync(filename)){
            fs.readFile(filename, function(err, data) {
                res.writeHead(200, {'Content-Type': 'text/html'});
                res.write(data.toString());
                return res.end();
            });
        }else{
            res.writeHead(404, {'Content-Type': 'text/html'});
            return res.end("404 Not Found @ "+access);
        }
    }else if(access==="/"){
        filename = "/Users/marksong/Project/tsinglan_gpa/index.html"
        log(access_ip,"want to read "+filename)
        if(fs.existsSync(filename)){
            fs.readFile(filename, function(err, data) {
                res.writeHead(200, {'Content-Type': 'text/html'});
                res.write(data.toString());
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