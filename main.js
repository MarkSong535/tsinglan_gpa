var http = require('http');
var url = require('url');
var util = require('util');

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


http.createServer(function(req, res) {
    res.writeHead(200, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    });


    var params = url.parse(req.url, true).query;

    if ((!params) || (!params.name) || (!params.sid)) {
        res.write("{\"err\": true, \"status\": true}");
        res.end();
        console.log(formatDate(new Date())+" lack of info")
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
                data_string += '\n' +
                    params.name + ' ' + params.sid + ' ';
                data_string += formatDate(new Date());
                console.log(data_string);
            } else {
                res.write("{\"err\": true, \"status\": true}");
                console.log(formatDate(new Date())+" bad python")
            }
            res.end();
        });
    }


}).listen(3000);