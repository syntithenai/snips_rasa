#!/opt/rasa/anaconda/bin/python
# -*-: coding utf-8 -*-
""" Snips core and nlu server. """

import json
import time
import os

from socket import error as socket_error

import paho.mqtt.client as mqtt

from thread_handler import ThreadHandler

from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.converters import load_data
from rasa_nlu.model import Metadata, Interpreter

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging

import sys
import warnings

from rasa_core import utils
from rasa_core.actions import Action
from rasa_core.agent import Agent
from rasa_core.channels.console import ConsoleInputChannel
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.policies.memoization import MemoizationPolicy

logger = logging.getLogger(__name__)

# Creates a blocking mqtt listener that can take one of three actions
# - train the nlu and the dialog manager and reload them
# - respond to nlu query on mqtt hermes/nlu/query with a message to hermes/nlu/intentParsed
# - respond to intents eg nlu/intent/User7_dostuff by calling code
class RasaServer():
    
    def __init__(self,
                 mqtt_hostname='mosquitto',
                 mqtt_port='1883',
                 nlu_model_path='models/nlu/',
                 #default/current',
                 dialog_model_path='models/dialog',
                 config_file='config/config.json',
                 domain_file='config/domain.yml',
                 nlu_training_file='config/nlu.md',
                 dialog_training_file='config/stories.md'
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
        # RASA config
        self.nlu_model_path = nlu_model_path
        self.dialog_model_path = nlu_model_path
        self.config_file = config_file
        # RASA training config
        self.domain_file = domain_file
        self.nlu_training_file = nlu_training_file
        self.dialog_training_file = dialog_training_file
        self.loadModels()

    # RASA model generation
    def loadModels(self):
        # if file exists import os.path os.path.exists(file_path)
        # create an NLU interpreter and dialog agent based on trained models
        self.interpreter = Interpreter.load("{}/default/current".format(self.nlu_model_path), RasaNLUConfig(self.config_file))
        #self.interpreter = RasaNLUInterpreter("models/nlu/default/current")
        self.agent = Agent.load(self.dialog_model_path, interpreter=self.interpreter)

        print('loaded model')


    # these function read extended rasa stories format and output something suitable for training
    def generateNLU(self):
        pass
    def generateDialog(self):
        pass
    def generateDomain(self):
        pass


    # RASA training
    def train_dialogue(domain_file=self.domain_file,
                   model_path=self.dialog_model_path,
                   training_data_file=self.dialog_training_file):
        agent = Agent(domain_file,
                      policies=[MemoizationPolicy(), DefaultPolicy()])
        agent.train(
                training_data_file,
                max_history=3,
                epochs=100,
                batch_size=50,
                augmentation_factor=50,
                validation_split=0.2
        )
        agent.persist(model_path)
        return agent

    def train_nlu():
        from rasa_nlu.converters import load_data
        from rasa_nlu.config import RasaNLUConfig
        from rasa_nlu.model import Trainer

        training_data = load_data(self.nlu_training_file)
        trainer = Trainer(RasaNLUConfig(self.config_file))
        trainer.train(training_data)
        #model_directory = trainer.persist('models/nlu/', fixed_model_name="current")
        model_directory = trainer.persist(self.nlu_model_path, fixed_model_name="current")
        return model_directory





    # MQTT LISTENING SERVER
    def start(self):
        self.thread_handler.run(target=self.start_blocking)
        self.thread_handler.start_run_loop()

    def start_blocking(self, run_event):
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
        # SUBSCRIBE 
        self.client.subscribe('#', 0)
        while run_event.is_set():
            try:
                self.client.loop()
            except AttributeError as e:
                self.log("Error in mqtt run loop {}".format(e))
                time.sleep(1)

    def on_connect(self, client, userdata, flags, result_code):
        self.log("Connected with result code {}".format(result_code))

    def on_disconnect(self, client, userdata, result_code):
        self.log("Disconnected with result code " + str(result_code))
        time.sleep(5)
        self.thread_handler.run(target=self.start_blocking)

    def on_message(self, client, userdata, msg):
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
                    qos=0,
                    retain=False)
    def log(self, message):
       print (message)
    #def run(serve_forever=True):
        #interpreter = RasaNLUInterpreter("models/nlu/default/current")
        #agent = Agent.load("models/dialogue", interpreter=interpreter)

        #if serve_forever:
            ##agent.handle_channel(ConsoleInputChannel())
            ## agent.handle_message(msg)
        #return agent


    #if __name__ == '__main__':
        #utils.configure_colored_logging(verbose=True)

        #parser = argparse.ArgumentParser(
                #description='starts the bot')

        #parser.add_argument(
                #'task',
                #choices=[ "train-dialogue", "run"],
                #help="what the bot should do - e.g. run or train?")
        #task = parser.parse_args().task

        ## decide what to do based on first parameter of the script
        ##if task == "train-nlu":
            ##train_nlu()
        ##el
        #if task == "train-dialogue":
            #train_dialogue()
        #elif task == "run":
            #run()
        #else:
            #warnings.warn("Need to pass either 'train-nlu', 'train-dialogue' or "
                          #"'run' to use the script.")
            #exit(1)
       
       
       



#server = RasaNLUServer(os.environ['MQTT_HOST'], os.environ['MQTT_PORT'],os.environ['NLU_MODEL_FOLDER'],os.environ['NLU_CONFIG_FILE'])
#server.start()












#class ActionSearchRestaurants(Action):
    #def name(self):
        #return 'action_search_restaurants'

    #def run(self, dispatcher, tracker, domain):
        #dispatcher.utter_message("here's what I found")
        #return []


#class ActionSuggest(Action):
    #def name(self):
        #return 'action_suggest'

    #def run(self, dispatcher, tracker, domain):
        #dispatcher.utter_message("papi's pizza place")
        #return []


class DefaultPolicy(KerasPolicy):
    def model_architecture(self, num_features, num_actions, max_history_len):
        """Build a Keras model and return a compiled model."""
        from keras.layers import LSTM, Activation, Masking, Dense
        from keras.models import Sequential

        n_hidden = 32  # size of hidden layer in LSTM
        # Build Model
        batch_shape = (None, max_history_len, num_features)

        model = Sequential()
        model.add(Masking(-1, batch_input_shape=batch_shape))
        model.add(LSTM(n_hidden, batch_input_shape=batch_shape))
        model.add(Dense(input_dim=n_hidden, output_dim=num_actions))
        model.add(Activation('softmax'))

        model.compile(loss='categorical_crossentropy',
                      optimizer='adam',
                      metrics=['accuracy'])

        logger.debug(model.summary())
        return model









