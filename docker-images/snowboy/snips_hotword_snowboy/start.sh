#!/bin/sh
cp -r /opt/snowboy/* /opt/snips_hotword_snowboy/
cd /opt/snips_hotword_snowboy/
#/opt/rasa/anaconda/bin/
python /opt/snips_hotword_snowboy/server.py 
#2&> /tmp/snowboylog/log
#sleep 36000
