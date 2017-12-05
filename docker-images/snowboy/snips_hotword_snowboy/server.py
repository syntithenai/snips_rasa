# -*-: coding utf-8 -*-
""" Snips hotword server. """

import json
import time
import os
import syslog
import sys
import wave
import struct
import StringIO

from socket import error as socket_error

import paho.mqtt.client as mqtt


sys.path.append('')

import snowboydecoder


    
class SnowboyHotwordServer():
    """ Snips hotword server. """

    def __init__(self,
                 mqtt_hostname='mosquitto',
                 mqtt_port=1883,
                 hotword_model='resources/snowboy.umdl',
                 hotword='snowboy',
                 site='default',
                 listen_to='default'
                 ):
                     
        self.activeClientList = []
        self.allowedClientList = listen_to.split(',')
        self.messageCount = 0;
        self.detection = snowboydecoder.HotwordDetector(hotword_model, sensitivity=0.9)

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        
        self.mqtt_hostname = mqtt_hostname
        self.mqtt_port = mqtt_port
        self.hotword = hotword
        self.hotword_model = hotword_model
        self.site = site
        self.listen_to = listen_to
        
    def start(self):
        self.log("Connecting to {} on port {}".format(self.mqtt_hostname, str(self.mqtt_port)))
        retry = 0
        while True :
            try:
                self.log("Trying to connect to {}".format(self.mqtt_hostname))
                self.client.connect(self.mqtt_hostname, self.mqtt_port, 60)
                break
            except (socket_error, Exception) as e:
                self.log("MQTT error {}".format(e))
                time.sleep(5 + int(retry / 5))
                retry = retry + 1
        
        while True:
            try:
                self.client.loop()
            except AttributeError as e:
                self.log("Error in mqtt run loop {}".format(e))
                time.sleep(1)

    def on_connect(self, client, userdata, flags, result_code):
        self.log("Connected with result code {}".format(result_code))
        self.client.subscribe('hermes/hotword/toggleOff')
        self.client.subscribe('hermes/hotword/toggleOn')
        for allowedClient in self.allowedClientList:
            self.client.subscribe('hermes/audioServer/{}/audioFrame'.format(allowedClient))
            self.client.subscribe('hermes/hotword/{}/toggleOff'.format(self.hotword))
            self.client.subscribe('hermes/hotword/{}/toggleOn'.format(self.hotword))
        # enable to start
        client.publish('hermes/hotword/{}/toggleOn'.format(self.hotword), payload="{\"siteId\":\"" + self.site + "\",\"sessionId\":null}", qos=0)
            

    def on_disconnect(self, client, userdata, result_code):
        self.log("Disconnected with result code " + str(result_code))
        time.sleep(5)
    
    def on_message(self, client, userdata, msg):
        if msg.topic.endswith('toggleOff'):
            self.log('toggle off')
            msgJSON = json.loads(msg.payload)
            siteId = msgJSON.get('siteId','default')
            if siteId in self.activeClientList:
                self.activeClientList.remove(siteId)
        elif msg.topic.endswith('toggleOn'):
            self.log('toggle on')
            msgJSON = json.loads(msg.payload)
            siteId = msgJSON.get('siteId','default')
            if siteId not in self.activeClientList:
                self.activeClientList.append(siteId)
            self.messageCount = 0;
        else:
            self.messageCount = self.messageCount + 1;
            siteId = msg.topic.split('/')
            if siteId[2] in self.activeClientList:
                #if self.messageCount % 20 == 0 :
                    #self.log('audiofrom {} {}'.format(siteId[2],len(msg.payload)))
                ##can test the speed
                #start = time.clock()

                #this works but is SLOWER than the below code
                #buffer = StringIO.StringIO(msg.payload)
                #wav = wave.open(buffer, 'r')
                #data = wav.readframes(wav.getnframes())
                
                #this is faster
                data = msg.payload[44:struct.unpack('<L', msg.payload[4:8])[0]]

                #elapsed_time = time.clock()
                #print (elapsed_time - start)
                
                ans = self.detection.detector.RunDetection(data)
                if ans == 1:
                    print('Hotword Detected!')
                    client.publish('hermes/hotword/{}/detected'.format(self.hotword), payload="{\"siteId\":\"" + siteId[2] + "\",\"sessionId\":null}", qos=0)
        
        
        
    def log(self, message):
        print(message)

server = SnowboyHotwordServer()
server.start()
