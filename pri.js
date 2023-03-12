const fs = require('fs');
const config_data = JSON.parse(fs.readFileSync("config.json",'utf8'))
const hostname = "pri.tsinglan.live"
const port = config_data["port"]+99;
var http = require('http');
var url = require('url');
const exec = require("child_process").exec;

pwd = config_data['Father directory']

http.createServer(function(req, res) {
    console.log(req.headers.host)
	if (req.headers.host !== hostname) {
        filename = pwd + "jump_pri.html"
        if (fs.existsSync(filename)) {
            fs.readFile(filename, function(err, data) {
                res.writeHead(200, {
                    'Content-Type': 'text/html'
                });
                res.write(data);
                return res.end();
            });
        }
    }else{
        module.exports = function myTest() {
    
            return new Promise(function(resolve, reject) {
                res.writeHead(200, {
                    'Content-Type': 'text/html'
                });
                var cmd = 'python ' + pwd + 'pri.py';
                console.log(cmd)
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
                        res.write(stdout);
                        return res.end();
                        
                        resolve();
                    }
                });
            });
        };
        module.exports()
    }
}).listen(port);
