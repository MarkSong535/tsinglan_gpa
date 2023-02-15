var http = require('http');
var url = require('url');
var util = require('util');

http.createServer(function(req, res) {
    res.writeHead(200, {
        'Content-Type': 'application/json'
    });


    var params = url.parse(req.url, true).query;

    if ((!params) || (!params.name) || (!params.sid)) {
        res.write("{\"err\": true, \"status\": true}");
        res.end();
    } else {
        console.log('python3 /root/course/score.py ' + params.name + ' ' + params.sid)
        const {
            spawn
        } = require('child_process')

        const command = spawn('python3 /root/course/score.py ' + params.name + ' ' + params.sid, {
            shell: true
        })

        command.stdout.on('data', data => {
            data_string = data.toString();
            if (data_string.charAt(0) == '{') {
                res.write(data_string);
            } else {
                res.write("{\"err\": true, \"status\": true}");
            }
            res.end();
        });
    }


}).listen(3000);