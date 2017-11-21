#!/opt/rasa/anaconda/bin/python

# -*-: coding utf-8 -*-
""" Snips core server. """

import json
import time
import os
import syslog

from socket import error as socket_error

import paho.mqtt.client as mqtt

from thread_handler import ThreadHandler

from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.converters import load_data
from rasa_nlu.model import Metadata, Interpreter

import sys
sys.path.append('')

import snowboydecoder
import snowboythreaded

import signal

    
class SnowboyHotwordServer():
    """ Snips hotword server. """

    def __init__(self,
                 mqtt_hostname,
                 mqtt_port,
                 hotword,
                 site
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
        self.hotword = hotword
        self.site = site
        self.active = True
        # listen for hotword
        self.model = os.environ['HOTWORD_MODEL']
        
        # capture SIGINT signal, e.g., Ctrl+C
        #signal.signal(signal.SIGINT, signal_handler)
        self.interrupted = False
        signal.signal(signal.SIGINT, self.signal_handler)
        self.log('starting')
        #self.detector = snowboydecoder.HotwordDetector(self.model, sensitivity=0.5)
        #self.detector = snowboythreaded.ThreadedDetector(self.model, sensitivity=0.5)
        #self.log('created')
        #self.detector.start()
        #self.log('started')
        ##self.hotword_on()
        
        
    def start(self):
        """ Start the MQTT client. """
        self.thread_handler.run(target=self.start_blocking)
        self.thread_handler.start_run_loop()

    def start_blocking(self, run_event):
        """ Start the MQTT client, as a blocking method.

        :param run_event: a run event object provided by the thread handler.
        """
        self.log("Connecting to {} on port {}".format(self.mqtt_hostname, str(self.mqtt_port)))

        retry = 0
        while True and run_event.is_set():
            try:
                self.log("Trying to connect to {}".format(self.mqtt_hostname))
                self.client.connect(self.mqtt_hostname, self.mqtt_port, 60)
                break
            except (socket_error, Exception) as e:
                self.log("MQTT error {}".format(e))
                time.sleep(5 + int(retry / 5))
                retry = retry + 1
        
        while run_event.is_set() and not self.interrupted:
            try:
                self.client.loop()
            except AttributeError as e:
                self.log("Error in mqtt run loop {}".format(e))
                time.sleep(1)

    # pylint: disable=unused-argument,no-self-use
    def on_connect(self, client, userdata, flags, result_code):
        """ Callback when the MQTT client is connected.

        :param client: the client being connected.
        :param userdata: unused.
        :param flags: unused.
        :param result_code: result code.
        """
        self.log("Connected with result code {}".format(result_code))
        self.client.subscribe('#', 0)
        time.sleep(1)
        #self.send_message('hermes/hotword/toggleOn','')
        

    # pylint: disable=unused-argument
    def on_disconnect(self, client, userdata, result_code):
        """ Callback when the MQTT client is disconnected. In this case,
            the server waits five seconds before trying to reconnected.

        :param client: the client being disconnected.
        :param userdata: unused.
        :param result_code: result code.
        """
        self.log("Disconnected with result code " + str(result_code))
        time.sleep(5)
        self.thread_handler.run(target=self.start_blocking)

    # pylint: disable=unused-argument
    def on_message(self, client, userdata, msg):
        """ Callback when the MQTT client received a new message.

        :param client: the MQTT client.
        :param userdata: unused.
        :param msg: the MQTT message.
        """
        #self.log('message')
        #self.log("New message on topic {}".format(msg.topic))
        #self.log(client)
        #self.log(userdata)
        #self.log(msg.payload)
        #if msg.payload is None or len(msg.payload) == 0:
            #pass
        if msg.topic is not None and msg.topic.startswith("hermes/hotword/"):
        #and msg.payload:
            if msg.topic.endswith('toggleOff'):
                self.log('toggle off')
                payload = {'siteId':'default'}
                try:
                    payload = json.loads(msg.payload.decode('utf-8'))
                except ValueError as e:
                    self.log("No message content {}".format(e))
                self.log('payload')
                if 'siteId' in payload:
                    self.log('siteid')
                    if payload['siteId'] == self.site:
                        self.log('siteid match')
                        #self.site = payload.siteId
                        self.hotword_off()
                else:
                    self.hotword_off()
            elif msg.topic.endswith('toggleOn'):
                self.hotword_on()
                
    def hotword_off(self):
        self.log('hotword off')
        self.active = True
        #self.detector = snowboydecoder.ThreadedDetector(self.model, sensitivity=0.5)
        # snowboydecoder.ding_callback()
        # main loop
        self.interrupted = False
        #self.detector = snowboythreaded.ThreadedDetector(self.model, sensitivity=0.5)
        #self.detector(star)
        #self.detector.start_recog(detected_callback=self.send_detected,sleep_time=0.03)
        #detected_callback=self.send_detected,
               #interrupt_check=self.interrupt_callback,
        #self.detector = snowboydecoder.HotwordDetector(self.model, sensitivity=0.5)
        #self.detector.start(detected_callback=self.send_detected, interrupt_check=self.interrupt_callback,sleep_time=0.03)
        self.detector = snowboythreaded.ThreadedDetector(self.model, sensitivity=0.5)
        self.log('created')
        self.detector.start()
        self.log('started')
        self.detector.start_recog(detected_callback=self.send_detected,sleep_time=0.03)
        self.log('hotword started')
        
    def hotword_on(self):
        self.log('hotword on')
        self.active = True
        #self.interrupted = True;
        #if self.detector is not None:
        #    self.detector.pause_recog()
        #self.detector.terminate()
        #self.detector = None                    
    
    def signal_handler(self,signal=None, frame=None):
        self.interrupted = True
        self.active = False
        raise Exception('Interrupted !')


    def send_detected(self):
        self.log('send detected')
        snowboydecoder.play_audio_file()
        #topic = 'hermes/hotword/{}/detected'.format(self.hotword)
        topic = 'hermes/hotword/detected'
        payload = json.dumps({"siteId": self.site})
        self.log(payload)
        self.send_message(topic,payload)
        # ?? should come from dialog service
        #self.hotword_off()
    
    def interrupt_callback(self,value=None):
        #self.log('hotword exit check')
        return False
        # self.active
        #self.interrupted    
            
        
    def send_message(self,topic,payload):
        self.log('send message')
        self.client.publish(topic,
                    payload, 
                    qos=0,
                    retain=False)
        
        
        #self.log('send message')
        #self.client.publish(topic,payload,qos=0,retain=False)
        #self.log('sent message to {}'.format(topic))
      
    def log(self, message):
        print(message)
        file = open("/tmp/snowboylog/log","a") 
        try:
            file.write(message) 
        except TypeError as e:
            pass
        file.write("\n")
        file.close()
 #       syslog.syslog('Processing started')
#       syslog.syslog(syslog.LOG_ERR,message)
       

server = SnowboyHotwordServer(os.environ['MQTT_HOST'], os.environ['MQTT_PORT'],os.environ['HOTWORD_ID'],os.environ['SITE_ID'])

server.start()
