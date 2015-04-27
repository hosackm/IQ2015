var express = require('express');
var nunjucks = require('nunjucks');

var app = express();
var port = process.argv[2] || 8080;

nunjucks.configure('views', {autoescape: true, express: app});

app.use(express.static('public'));
app.use('/', function(req, res){
  res.render('index.html', {});
});

console.log("Express server running on port: ", port);
app.listen(port);
