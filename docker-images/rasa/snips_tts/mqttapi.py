from threading import Thread
import json
from functions import tts



class MQTTApi(Api):

    def __init__(self):
        super(MQTTApi, self).__init__('mqtt_api')

    #@classmethod
    def publish_item(self, topic, message=None):
        #log.info("MQTT Published - Topic: {} Message: {}".format(topic,message))
        self.client.publish(topic, payload=message, qos=1)

    def on_connect(client, userdata, rc):
        #log.debug("MQTT connected with result code " + str(rc))
        client.subscribe("hermes/tts/say")
        client.subscribe("hermes/audioServer/+/playFinished")
        client.subscribe("hermes/intent/#")
        client.subscribe("hermes/nlu/intentParsed")


    def on_message(client, userdata, msg):
        if msg.topic == 'hermes/tts/say':
            t = Thread(target=tts.speak, args=( msg.payload,))
            t.start()   
