var express = require('express');
var app     = express();
var server  = require('http').createServer(app);
var io      = require('socket.io').listen(server);
var nunjucks = require('nunjucks');
var zmq = require('zmq');
var zmqsock = zmq.socket('pull');
var port = process.argv[2] || 8080;
var rpi = process.argv[3] || 'tcp://127.0.0.1:7777';

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
  console.log('socket.io connection made');
  zmqsock.connect(rpi);
  zmqsock.on('message', function(msg){
    var m = msg.toString();
    var msgtype = m.charAt(0);
    m = m.substr(1);
    
    if(msgtype === 'l')
      socket.emit('loudness', m);
    else
      socket.emit('fft', m);
  });
});

console.log("Express server running on port: ", port);
server.listen(port);
