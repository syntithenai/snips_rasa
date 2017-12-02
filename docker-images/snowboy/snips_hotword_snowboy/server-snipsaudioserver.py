# author Greg<kiza.soza@gmail.com>

import snowboydecoder
import sys
import wave
import paho.mqtt.client as mqtt
import struct
import StringIO
import json
import time

mqtt_client = mqtt.Client()

clientList = []
allowedClientList = ['zero', 'kitchen']

sensitivity = 0.4
detection = snowboydecoder.HotwordDetector('Hey_Janet.pmdl', sensitivity=sensitivity)


def on_connect(client, userdata, flags, rc):
    for allowedClient in allowedClientList:
        mqtt_client.subscribe('hermes/audioServer/{}/audioFrame'.format(allowedClient))
    mqtt_client.subscribe('hermes/hotword/toggleOff')
    mqtt_client.subscribe('hermes/hotword/toggleOn')

def on_message(client, userdata, msg):
    if msg.topic == 'hermes/hotword/toggleOff':
        msgJSON = json.loads(msg.payload)
        if msgJSON['siteId'] not in clientList:
            clientList.append(msgJSON['siteId'])
    elif msg.topic == 'hermes/hotword/toggleOn':
        msgJSON = json.loads(msg.payload)
        clientList.remove(msgJSON['siteId'])
    else:
        siteId = msg.topic.split('/')
        if siteId[2] not in clientList:
            #can test the speed
            #start = time.clock()

            #this works but is SLOWER than the below code
            #buffer = StringIO.StringIO(msg.payload)
            #wav = wave.open(buffer, 'r')
            #data = wav.readframes(wav.getnframes())
            
            #this is faster
            data = msg.payload[44:struct.unpack('<L', msg.payload[4:8])[0]]

            #elapsed_time = time.clock()
            #print (elapsed_time - start)
            
            ans = detection.detector.RunDetection(data)
            if ans == 1:
                print('Hotword Detected!')
                clientList.append(siteId[2])
                client.publish('hermes/hotword/default/detected', payload="{\"siteId\":\"" + siteId[2] + "\",\"sessionId\":null}", qos=0)


if __name__ == '__main__':
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect('10.0.1.22', 1883)
    mqtt_client.loop_forever()```
