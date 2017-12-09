#!/opt/rasa/anaconda/bin/python
# -*-: coding utf-8 -*-
""" Snips core server. """

import json
import time
import os

from socket import error as socket_error

import paho.mqtt.client as mqtt

from thread_handler import ThreadHandler

from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.converters import load_data
from rasa_nlu.model import Metadata, Interpreter



class RasaNLUServer():
    """ Snips core server. """

    def __init__(self,
                 mqtt_hostname,
                 mqtt_port,
                 nlu_model_path,
                 config_path
                 ):
        """ Initialisation.

        :param config: a YAML configuration.
        :param assistant: the client assistant class, holding the
                          intent handler and intents registry.
        """
        self.thread_handler = ThreadHandler()
        print('model')
        print(nlu_model_path)
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.mqtt_hostname = mqtt_hostname
        self.mqtt_port = mqtt_port
        self.nlu_model_path = nlu_model_path
        self.config_path = config_path
        # create an NLU interpreter based on trained NLU model
        self.interpreter = Interpreter.load(self.nlu_model_path, RasaNLUConfig(self.config_path))
        print('loaded model')


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
        self.client.subscribe('#', 0)
        while run_event.is_set():
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
        #self.log(client)
        #self.log(userdata)
        #self.log(msg.payload)
        if msg.payload is None or len(msg.payload) == 0:
            pass
        if msg.topic is not None and msg.topic.startswith("hermes/nlu") and msg.topic.endswith('/query') and msg.payload:
            self.log("New message on topic {}".format(msg.topic))
            payload = json.loads(msg.payload.decode('utf-8'))
            print(payload)
            if 'input' in payload :
                sessionId = payload['sessionId']
                id = payload['id']
                text = payload['input']
                print(text)
                if (text == "restart server"):
                    print('restart server')
                    self.interpreter = Interpreter.load(self.nlu_model_path, RasaNLUConfig(self.config_path))
                else:
                    lookup = self.interpreter.parse(text)
       
                    slots=[]
                    
                    for entity in lookup['entities']:
                        slot = {"entity": entity['value'],"range": {"end": entity['end'],"start": entity['start']},"rawValue": entity['value'],"slotName": "entity","value": {"kind": "Custom","value": entity['value']}} 
                        slots.append(slot)
                    print(slots)
                    intentName = "user_Kr5A7b4OD__{}".format(lookup['intent']['name'])
                    self.client.publish('hermes/nlu/intentParsed',
                    payload=json.dumps({"id": id,"sessionId": sessionId, "input": text,"intent": {"intentName": intentName,"probability": 1.0},"slots": slots}), 
                # 
                    qos=0,
                    retain=False)
    def log(self, message):
       print (message)



server = RasaNLUServer(os.getenv('MQTT_HOST','mosquitto'), os.getenv('MQTT_PORT','1883'),os.getenv('NLU_MODEL_FOLDER','/opt/rasa/data/nlu-model/default/model_20171125-071720'),os.getenv('NLU_CONFIG_FILE','/opt/rasa/data/nlu-model/config.json'))
server.start()
