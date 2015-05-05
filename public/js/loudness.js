//Loudness Plot
// Global variables. yuck!
var lsamps = [0, 1, 2, 3];
var lcur = 0;
var fftsamps = [];
var socket = io.connect('http://localhost:8080');
// var socket = io.connect('http://169.254.229.123:8080');
var lseries = new TimeSeries();

var loudchart = new SmoothieChart({
  maxValue:-10,
  minValue:-40,
  timestampFormatter:SmoothieChart.timeFormatter
});
loudchart.addTimeSeries(lseries, {
  strokeStyle: 'rgba(0, 255, 0, 1)',
  fillStyle: 'rgba(0, 255, 0, 0.2)',
  lineWidth: 4
});
loudchart.streamTo(document.getElementById("smoothie-chart"), 0);

// Recieve Loudness data
socket.on('loudness', function(data){
  if(!data)
    return;

  // parse/update global values
  // Ex. data = {value: 24};
  data = JSON.parse(data);
  lcur = data.value;
  lsamps.push(lcur);
  lseries.append(new Date().getTime(), lcur);
  // $("#louddisplay").text(lcur);
});

// Recieve FFT Data
socket.on('fft', function(data){
  if(!data)
    return;

  //console.log(data);

  // Ex. data = {length: 1024, samples: [0.0, 1.3, ... , 45.0]};
  data = JSON.parse(data);
  var l = data.nsamp;
  fftsamps = data.samples;
  
  // make list of dataPoints
  var points = fftsamps.reduce(function(prev, cur, i, arr){
    if (i >= arr.length - 1)
      return prev;
    prev.data.push({x: i, y: cur});
    return prev;
  }, {data: []});

  var chart = new CanvasJS.Chart("fft-chart",
  {
    title: {text: "FFT Plot"},
    width: 1310,
    height: 500,
    animationEnabled: true,
    axisX:{title: "Frequency (Hz)", minimum:20, maximum:20000},//, interval: 3},
    axisY:{title: "Magnitude (dB)", minimum:0, maximum:150},
    legend: {},
    data: [{
      name: 'fft1',
      type: 'area',
      color: 'rgba(0, 255, 0, 1)',
      markerSize: 0,
      dataPoints: points.data
    }]
  });
  //chart.options.data[0].dataPoints = points.data;
  //chart.update();

  chart.render();
  $(".canvasjs-chart-credit").remove();
});

// Button Clicking Shhhhtuff
$("#switchview").click(function(){
  if($("#switchview").text() === "View FFT"){
    $("#loudplot").addClass("hidden");
    $("#fftplot").removeClass("hidden");
    $("#switchview").text("View Loudness");
  }
  else{
    $("#fftplot").addClass("hidden");
    $("#loudplot").removeClass("hidden");
    $("#switchview").text("View FFT");
  }
});
