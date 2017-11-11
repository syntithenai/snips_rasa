angular.module('rasaUIApp').component('microphone', {
	template: '<span class="float-right" ng-click="$ctrl.switchRecognition()" ><button id="voicerecognitionbutton" style="border-color:{{$ctrl.microphoneBorderColor}}"   class="status-{{$ctrl.microphoneStatus}} fi-microphone" ></button></span><hgroup class="speech-bubble float-right"><h4>CSS speech bubbles made easy!</h4></hgroup>',
	//<img id="loadingimage" ng-show="actionPending" src='images/loader.gif'  />
	bindings: { host: '@',port: '@' },
	controller: function MicrophoneController() {
		this.logs = ['starting'];
		this.microphoneStatus=2;
		this.microphoneBorderColor='red';
		this.host='';
		this.port='';
		this.client = null;
		var self=this;
		
		
		function switchRecognition() {
			console.log(['SEND MESSAGE']);
			// off
			if (self.recognitionStatus == 0) {
				sendMessage('hermes/hotword/toggleOff','');
				sendMessage('hermes/asr/toggleOn','');
			// hotword active
			} else if (self.recognitionStatus == 1) {
				sendMessage('hermes/hotword/toggleOff','');
				sendMessage('hermes/asr/toggleOn','');
			// asr active
			} else if (self.recognitionStatus == 2) {
				sendMessage('hermes/asr/toggleOff','');
				sendMessage('hermes/hotword/toggleOn','');
			}
		} 

		// send a message to the mqqt queue
		function sendMessage(destination,text) {
			message = new Paho.MQTT.Message(text);
			message.destinationName = destination; //"hermes/announce";
			self.client.send(message);
			console.log(['SENT MESSAGE',destination,text]);
		}
	
		this.$onInit=function(){
			/*****************************************************/
			// UI clicks
			/*****************************************************/
		
			/*****************************************************/
			// PAHO mqqt client
			/*****************************************************/
			console.log(["create client",this.host,this.port]);
			self.client = new Paho.MQTT.Client(this.host, Number(this.port), "clientId");
			console.log("created client");
			//client = new Paho.MQTT.Client('localhost', Number(9002), "clientId");

			// set callback handlers
			self.client.onConnectionLost = onConnectionLost;
			self.client.onMessageArrived = onMessageArrived;

			// connect the client
			self.client.connect({onSuccess:onConnect});
			console.log("create client connected");

			// called when the client connects
			function onConnect() {
			  // Once a connection has been made, make a subscription and send a message.
			  console.log(["onConnect",this.client]);
			  self.client.subscribe("#");
			}
			


			// called when the client loses its connection
			function onConnectionLost(responseObject) {
			  if (responseObject.errorCode !== 0) {
				console.log("onConnectionLost:"+responseObject.errorMessage);
				setTimeout(function() {
					self.client.connect({onSuccess:onConnect});
				},3000);
			  }
			}

			function flashMessage(text) {
				console.log(['FLASH',text]);
			}

			// called when a message arrives
			function onMessageArrived(message) {
				//console.log(message);
				//console.log("onMessageArrived:"+message.topic + ' ' + message.payloadString);
				var payload = {};
				try {
					payload = JSON.parse(message.payloadString);
				} catch (e) {
					
				}
				//console.log(payload);
				var topicParts = message.topic.split('/');
				if (topicParts.length == 3) {
					if (topicParts[0] == "hermes") {
						console.log('HERMES');
						if (topicParts[1] == "hotword") {
							console.log('HOTWORD');
							if (topicParts[2] == "detected") {
								console.log('ON');
								self.microphoneStatus = 2; // listening
							} else if (topicParts[2] == "toggleOff") {
								console.log('OFF');
								//self.microphoneStatus = 0; //  off
							} 
						} else if (topicParts[1] == "asr") {
							console.log('ASR');
							if (topicParts[2] == "toggleOn") {
								console.log('ON');
								self.microphoneStatus = 2; // active
							} else if (topicParts[2] == "toggleOff") {
								console.log('OFF');
								self.microphoneStatus = 1; // off
							} else if (topicParts[2] == "textCaptured") {
								console.log('TEXT');
								flashMessage(payload.text);
							} 
						} else if (topicParts[1] == "audioServer" && topicParts[2] == "playFinished" ) {
							console.log(['AUDIOSERVER',payload]);
							
							// test filePath for start_of_input,end_of_input
						}
					} else {
						console.log('ERR NOT HERMES');
					}
				} else {
					console.log('ERR NOT THREE PARTS TO TOPIC');
				}
				// hotword detected set microphone status
				//  hermes/hotword/toggleOff
				//  hermes/hotword/toggleOn
				//  hermes/hotword/detected
				//  hermes/hotword/wait
				//  hermes/asr/toggleOff
				//  hermes/asr/toggleOn
				//  hermes/asr/textCaptured
				// hermes/nlu/toggleOff
				// hermes/nlu/toggleOn
				// hermes/audioServer/playFile
				// hermes/audioServer/playFinished
				// { "filePath": "/usr/share/snips/dialogue/sound/start_of_input.wav"}
				// hermes/audioServer/playFile
				// { "filePath": "/usr/share/snips/dialogue/sound/end_of_input.wav"}
				
				  // nlu
					// - broadcast snips.nlu event
					// - enact any bound commands
				  //  hermes/nlu/query
				  // asr
					// - broadcast snips.asr event
			}
		}


	}
});
