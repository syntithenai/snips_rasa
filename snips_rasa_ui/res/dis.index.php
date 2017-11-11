<html>
<head>
  <title>test Ws mqtt.js</title>
</head>
<body>
<script src="paho-mqtt.js"></script>
<script>
// PAHO
// Create a client instance
client = new Paho.MQTT.Client('192.168.1.138', Number(1884), "clientId");
//client = new Paho.MQTT.Client('localhost', Number(9002), "clientId");

// set callback handlers
client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

// connect the client
client.connect({onSuccess:onConnect});


// called when the client connects
function onConnect() {
  // Once a connection has been made, make a subscription and send a message.
  console.log("onConnect");
  client.subscribe("hermes/#");
  message = new Paho.MQTT.Message("Hello");
  message.destinationName = "hermes/announce";
  client.send(message);
}

// called when the client loses its connection
function onConnectionLost(responseObject) {
  if (responseObject.errorCode !== 0) {
    console.log("onConnectionLost:"+responseObject.errorMessage);
    setTimeout(function() {
		client.connect({onSuccess:onConnect});
	},3000);
  }
}

// called when a message arrives
function onMessageArrived(message) {
  console.log("onMessageArrived:"+message.payloadString);
}





// MQTT.JS
	//tcp://192.168.1.138:9898
  //var client = mqtt.connect('ws://192.168.1.138:1884'); //{ port: 9898, host: '192.168.1.138', keepalive: 10000}) // you add a ws:// url here
  //client.subscribe("hermes/#")

  //client.on("message", function (topic, payload) {
    //console.log([topic, payload].join(": "));
    //client.end();
  //})

  //client.publish("hermes/announce", "hello world!");
</script>
</body>
</html>
