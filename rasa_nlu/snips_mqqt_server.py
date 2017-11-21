# -*-: coding utf-8 -*-
""" Snips core server. """

import json
import time

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
        self.log("New message on topic {}".format(msg.topic))
        #self.log(client)
        #self.log(userdata)
        #self.log(msg.payload)
        if msg.payload is None or len(msg.payload) == 0:
            pass
        if msg.topic is not None and msg.topic.startswith("hermes/nlu/") and msg.payload:
            payload = json.loads(msg.payload.decode('utf-8'))
            if 'text' in payload:
                text = payload['text']
                    lookup = self.interpreter.parse(text)
       #             print(lookup)
       
                    slots=[]
                    
                    for entity in lookup['entities']:
                        slot = {"entity": entity['value'],"range": {"end": entity['end'],"start": entity['start']},"rawValue": entity['value'],"slotName": "entity","value": {"kind": "Custom","value": entity['value']}} 
                        slots.append(slot)
                    
                    intentName = "user_Kr5A7b4OD__{}".format(lookup['intent']['name'])
                    self.client.publish('hermes/nlu/intentParsed',
                    payload=json.dumps({"input": text,"intent": {"intentName": intentName,"probability": 1.0},"slots": slots}), 
                # 
                    qos=0,
                    retain=False)
    def log(self, message):
       print (message)



server = RasaNLUServer('mosquitto', 1883,'/opt/rasa/data/nlu-model/default/model','/opt/rasa/data/nlu-model/config.json')
server.start()
