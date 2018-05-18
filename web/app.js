
var express = require("express");
var fs = require('fs');
var cp = require('child_process')
var app = express();
app.use('/assets', express.static('static/assets'))

app.get('/', function(req, res){
    let index = fs.readFileSync('static/html/index.html', 'utf8')
    res.send(index)
});

app.get('/get_prediction', function(req, res){
    let house_id = req.query['id'];
    p = cp.spawnSync('python',
                     ['single_predict.py', house_id],
                    {cwd: "static/assets/result/"});

    res.sendFile(__dirname + "/static/assets/result/" + house_id + ".result.json")
});

app.listen(3000);