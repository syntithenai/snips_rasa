#!/opt/rasa/anaconda/bin/python
# -*-: coding utf-8 -*-
""" Snips core and nlu server. """
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import time
import os

from socket import error as socket_error

import paho.mqtt.client as mqtt

from thread_handler import ThreadHandler
import sys,warnings
# apt-get install sox libsox-fmt-all
import sox

# Creates a blocking mqtt listener that can take one of three actions
# - train the nlu and the dialog manager and reload them
# - respond to nlu query on mqtt hermes/nlu/query with a message to hermes/nlu/intentParsed
# - respond to intents eg nlu/intent/User7_dostuff by calling code
class SnipsTTSServer():
    
    def __init__(self,
                 mqtt_hostname='mosquitto',
                 mqtt_port=1883,
                 ):
        """ Initialisation.

        :param config: a YAML configuration.
        :param assistant: the client assistant class, holding the
                          intent handler and intents registry.
        """
        self.thread_handler = ThreadHandler()
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.mqtt_hostname = mqtt_hostname
        self.mqtt_port = mqtt_port
        
    # MQTT LISTENING SERVER
    def start(self):
        self.thread_handler.run(target=self.start_blocking)
        self.thread_handler.start_run_loop()
        # send audioFrames
        
        

    def start_blocking(self, run_event):
        self.log("Connecting TTS to {} on port {}".format(self.mqtt_hostname, str(self.mqtt_port)))
        retry = 0
        while True and run_event.is_set():
            try:
                self.log("Trying to connect TTS to {} {}".format(self.mqtt_hostname,self.mqtt_port))
                self.client.connect(self.mqtt_hostname, self.mqtt_port, 60)
                break
            except (socket_error, Exception) as e:
                self.log("MQTT error {}".format(e))
                time.sleep(5 + int(retry / 5))
                retry = retry + 1
        # SUBSCRIBE 
        self.client.subscribe('hermes/tts/say', 0)
        while run_event.is_set():
            try:
                self.client.loop()
            except AttributeError as e:
                self.log("Error in mqtt run loop {}".format(e))
                time.sleep(1)

    def on_connect(self, client, userdata, flags, result_code):
        self.log("Connected TTS with result code {}".format(result_code))

    def on_disconnect(self, client, userdata, result_code):
        self.log("Disconnected TTS with result code " + str(result_code))
        time.sleep(5)
        self.thread_handler.run(target=self.start_blocking)

    def on_message(self, client, userdata, msg):
        print("MESSAGEtts: {}".format(msg.topic))
            
        if msg.topic is not None and msg.topic=="hermes/tts/say":
            print("MESSAGE OK: {}".format(msg.topic))
            payload = json.loads(msg.payload)
            # .decode('utf-8')
            sessionId = payload.get('sessionId')
            siteId = payload.get('siteId','default')
            lang = payload.get('lang','en-GB')
            theId = sessionId
            fileName = '/tmp/speaking.wav'
            
            os.system('/usr/bin/pico2wave -w=' + fileName + ' "{}" '.format(payload.get('text')))
            #pubCommand = "mosquitto_pub -h " +self.mqtt_hostname+" -t 'hermes/audioServer/default/playBytes/0049a91e-8449-4398-9752-07c858234' -f '" + fileName + "'"
            #print(pubCommand)
            #os.system(pubCommand)
            
            fp = open(fileName)
            f = fp.read()
            topic = 'hermes/audioServer/{}/playBytes'.format(siteId)
            if theId is not None:
                topic = topic + '/{}'.format(theId[::-1])
            self.client.publish(topic, payload=bytes(f),qos=0)
            #print("PUBLISHED on " + topic)
            os.remove(fileName)
            
            
                    
    def log(self, message):
       print (message)
       
server = SnipsTTSServer()
server.start()







