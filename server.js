var express = require('express');
var app     = express();
var server  = require('http').createServer(app);
var io      = require('socket.io').listen(server);
var nunjucks = require('nunjucks');
var port = process.argv[2] || 8080;

// Configurations
nunjucks.configure('views', {autoescape: true, express: app});
app.use(express.static('public'));

// Routes
app.get('/', function(req, res){
  res.render('index.html', {});
});
app.get('/realtime', function(req, res){
  res.render('realtime.html', {});
});

// Socket.io Logic
io.on('connection', function (socket) {
  socket.emit('news', { hello: 'world' });
  socket.on('my other event', function (data) {
    console.log(data);
  });
});

console.log("Express server running on port: ", port);
server.listen(port);
