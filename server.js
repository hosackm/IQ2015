var express     = require('express');
var app         = express();
var server      = require('http').createServer(app);
var io          = require('socket.io').listen(server);
var nunjucks    = require('nunjucks');
var zmq         = require('zmq');

// Variables
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
app.get('/heatmap', function(req, res){
  res.render('heatmap.html', {});
});

// ZMQ Setup
var zmqsock = zmq.socket('pull');
zmqsock.bind(rpi);
console.log('zmq waiting on', rpi);

// Socket.io Logic
io.on('connection', function (socket) {
  console.log('socket.io connection made');
  zmqsock.on('message', function(msg){
    //console.log('received msg', msg.toString());
    msg = msg.toString();
    var msgtype = msg.charAt(0);
    msg = msg.substr(1);

    if(msgtype === 'l'){
      socket.emit('loudness', msg);
      return;
    }
    if(msgtype === 'f'){
      socket.emit('fft', msg);
      //console.log('sending fft msg');
      return;
    }
  });
});

console.log("Express server running on port: ", port);
server.listen(port);
