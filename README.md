# Snips Rasa

## Overview

!! This project is a work in progress. 

This repository is a collection of projects related to [Snips AI](http://snips.ai)  and [RASA AI](http://rasa.ai).


- Dockerfile to build an image containing necessary files for pulseaudio, snips, snowboy and rasa (snips_rasa). 
- docker-compose.yml file to start a suite including 
    - snips
    - replacement server for hotword detector using snowboy (snips_hotword_snowboy)
    - replacement server for NLU processor using rasa NLU (snips_rasa_nlu)
    
### WIP    
- pulseaudio server to share the sound.
- skills server using RASA core and story format described below to listen for hermes/nlu/intentParsed and take actions based on stories.
- web server with site for editing stories to generate rasa_nlu, rasa_core and snips stubs from a story.
    
## Quick Start

To get started 

- [Install docker](https://www.google.com.au/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=0ahUKEwiPkYafmt3XAhUKJZQKHU3DBO4QFggoMAA&url=https%3A%2F%2Fdocs.docker.com%2Fengine%2Finstallation%2F&usg=AOvVaw3LbZ234MXDYJLII4P-TXAZ)

- ```pip install docker-compose```
- ```git clone https://github.com/syntithenai/snips_rasa.git```
- ```cd snips_rasa```
- ```docker-compose up```

    
## Sound Configuration

In /etc/asound.conf, types dmix and dsnoop are fine for mixing/sharing device access across multiple services running natively but inside docker, the first container locks the sound device.

To allow multiple containers shared access to sound inside Docker it is possible to run pulseaudio.
Alsa supports pcm type pulseaudio which becomes the default when pulseaudio is installed so applications can just continue to access /dev/sound oblivious of anything beyond Alsa. (and nothing locks)

Pulseaudio could be run on the host or inside a container. In both cases, authenticated sharing is possible by volume mounting the cookie file (tcp) or the socket (unix)

 - /home/stever/.config/pulse/cookie:/root/.config/pulse/cookie
 - /tmp/pulse-socket:/tmp/pulse-socket 

All containers need pulseaudio installed to function as clients.
Enable by adding PULSE_HOST=ip address or socket path as an environment variable

- PULSE_SERVER=192.168.1.100
- PULSE_SERVER="unix:/run/user/"$USER_ID"/pulse/native"


    
## Roadmap

My goal is to better understand what is possible in conversational UI by developing a user interface that
brings together RASA story telling format and snips skills.

My previous experience develop a voice first music player using dialogflow was very command like

As a starting point a minimal text format.

- Many stories serve as the training data of what actions to take based on what intents are triggered.
- Each story starts with ##
- An interaction starts with a * and the name of the intent.
- Example sentences preceded by = follow (used to generate NLU config)
- Actions sentences preceded by - by default return the text and where the text starts with an _ are executed (snips skills)


Confirmations, Yes/No Response and Form Wizard stories and more are possible.



### For example
```

## play some music
* play music
  = gimme some tunes
  = play some music
  - ok playing some random music
  - _play_music
  

## play some jazz music
* play music [genre=pop]
  = i want to hear some pop music
  = play some pop music
  - ok playing some pop music
  - _play_music

## play music by artist
* play music [artist=Josh Woodward]
  = i want to hear something by Josh Woodward
  = play some music by Josh Woodward
  - ok playing some music by Josh Woodward
  - _play_music

## clear the playlist
* clear the playlist
  - do you really want to clear the playlist?
* agree
  - ok clearing the playlist
  - _clearplaylist

```


