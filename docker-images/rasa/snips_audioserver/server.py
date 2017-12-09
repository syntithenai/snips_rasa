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
import pyaudio
import wave
import io

from socket import error as socket_error

import paho.mqtt.client as mqtt

from thread_handler import ThreadHandler
import sys
import warnings

class SnipsAudioServer():
    
    def __init__(self,
                 mqtt_hostname='mosquitto',
                 mqtt_port=1883,
                 site='default'
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
        self.site = site
        
    # MQTT LISTENING SERVER
    def start(self):
        self.thread_handler.run(target=self.start_blocking)
        self.thread_handler.run(target=self.sendAudioFrames)
        self.thread_handler.start_run_loop()

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
        self.client.subscribe('hermes/audioServer/+/playBytes/+', 0)
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
        parts = msg.topic.split('/')
        if msg.topic.startswith("hermes/audioServer/") and parts[3] == 'playBytes' :
            siteId = parts[2]
            wf = wave.open(io.BytesIO(bytes(msg.payload)), 'rb')
            p = pyaudio.PyAudio()
            CHUNK = 256
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)

            data = wf.readframes(CHUNK)

            while data != None:
                stream.write(data)
                data = wf.readframes(CHUNK)

            stream.stop_stream()
            stream.close()

            p.terminate()
           
    def sendAudioFrames(self,run_event):
         
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1,
                        rate=16000, input=True,
                        frames_per_buffer=256)
        while True  and run_event.is_set():
            frames = stream.read(256)
            # generate wav file in memory
            output = io.BytesIO()
            waveFile = wave.open(output, "wb")
            waveFile.setnchannels(1)
            waveFile.setsampwidth(2)
            waveFile.setframerate(16000)
            waveFile.writeframes(frames) 
            #waveFile.close()
            topic = 'hermes/audioServer/{}/audioFrame'.format(self.site)
            self.client.publish(topic, payload=output.getvalue(),qos=0)
            #output.close()  # discard buffer memory
                    
    def log(self, message):
       print (message)
       
server = SnipsAudioServer()
server.start()







