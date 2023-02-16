var http = require('http');
var url = require('url');
var util = require('util');
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
        if(!params.type){
            console.log('python3 /Users/marksong/Project/tsinglan_gpa/score.py ' + params.name + ' ' + params.sid)
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
        }else{
            if(params.type==0){
                const {
                    spawn
                } = require('child_process')
    
                const command = spawn('echo \"' + params.name + ' ' + params.sid+'\" >> /Users/marksong/Project/tsinglan_gpa/transactions/requests', {
                    shell: true
                })
                console.log(formatDate(new Date())+' echo \"' + params.name + ' ' + params.sid+'\" >> /Users/marksong/Project/tsinglan_gpa/transactions/requests')
                // command.stdout.on('data', data => {
                //     console.log(formatDate(new Date())+" safe");
                //     res.write("{'rstatus':true}");
            
                //     res.end();
                // });
                command.stderr.on('data', data =>{
                    res.write("{\'rstatus\':true}");
                    res.end();
                    console.log(formatDate(new Date())+" error while writing");
                });
            }else if(params.type==1){
                res.write("fetch to proxy");
            }else{
                res.write("{'rstatus':false}");
            }
            res.end();
        }
    }


}).listen(3100);