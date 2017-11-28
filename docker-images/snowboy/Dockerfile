FROM syntithenai/snips_base
MAINTAINER Steve Ryan <stever@syntithenai.com>

COPY ./rpi-arm-raspbian-8.0-1.2.0.tar.bz2 /tmp/
COPY ./ubuntu1404-x86_64-1.2.0.tar.bz2 /tmp/

#RUN export DEBIAN_FRONTEND="noninteractive" ; apt-get  --allow-unauthenticated update && apt-get install -y pulseaudio swig3.0 python-pyaudio python3-pyaudio sox bzip2 nano python-pip ; 
#RUN  export DEBIAN_FRONTEND="noninteractive" ; apt-get  --allow-unauthenticated update && apt-get -f install && apt-get install  -fyq  --force-yes   virtualenv python-pip python-sklearn python-dev nano apt-transport-https wget dirmngr nano bzip2 git lsb-release supervisor init-system-helpers wget swig3.0 python-pyaudio python3-pyaudio sox python-pip git python-dev psutils pulseaudio libpcre3-dev portaudio19-dev  libatlas-base-dev  libpng12-0 libpng12-dev  libfreetype6 

#libfreetype6-dev 

RUN DEBIAN_FRONTEND="noninteractive" ; apt-get  --allow-unauthenticated update &&  apt-get install -y swig3.0 python-pyaudio python3-pyaudio sox python-pip

RUN apt-get install -y python-dev 

RUN pip install pyaudio; 
RUN apt-get install -y libatlas-base-dev pulseaudio
RUN pip install paho-mqtt
RUN mkdir -p /opt/snowboy && mkdir /tmp/snowboy && cd /tmp/snowboy && if [ `uname -m` = "armv7l" ]; then  bunzip2 /tmp/rpi-arm-raspbian-8.0-1.2.0.tar.bz2 && tar xf /tmp/rpi-arm-raspbian-8.0-1.2.0.tar; rpi-arm-raspbian-8.0-1.2.0 ; elif [ `uname -m` = "x86_64" ]; then bunzip2 /tmp/ubuntu1404-x86_64-1.2.0.tar.bz2 && tar xf /tmp/ubuntu1404-x86_64-1.2.0.tar;  cd ubuntu1404-x86_64-1.2.0; fi; cp -a * /opt/snowboy

COPY ./snips_hotword_snowboy/* /opt/snips_hotword_snowboy/
COPY ./snips_hotword_snowboy/resources/* /opt/snips_hotword_snowboy/resources/

COPY ./client.conf /etc/pulse/client.conf

ENTRYPOINT ["/opt/snips_hotword_snowboy/start.sh"]






















# https://s3-us-west-2.amazonaws.com/snowboy/snowboy-releases/rpi-arm-raspbian-8.0-1.2.0.tar.bz2
# https://s3-us-west-2.amazonaws.com/snowboy/snowboy-releases/ubuntu1404-x86_64-1.2.0.tar.bz2

# system dependancies
#RUN  export DEBIAN_FRONTEND="noninteractive" ; apt-get  --allow-unauthenticated update && apt-get -f install && apt-get install  -fyq  --force-yes   virtualenv python-pip python-sklearn python-dev nano apt-transport-https wget dirmngr nano bzip2 git lsb-release supervisor init-system-helpers wget swig3.0 python-pyaudio python3-pyaudio sox python-pip git python-dev psutils pulseaudio libpcre3-dev portaudio19-dev  libatlas-base-dev  libpng12-0 libpng12-dev  libfreetype6 libfreetype6-dev 
#  && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*;

# 


# SNOWBOY / RECENT SWIG

#RUN pip install pyaudio
#apt-get install libportaudio2 libportaudiocpp0 python-pyaudio python-dev

# download swig 3.0.12
#RUN wget -O /tmp/swig-3.0.12.tar.gz https://downloads.sourceforge.net/project/swig/swig/swig-3.0.12/swig-3.0.12.tar.gz?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fswig%2Ffiles%2Fswig%2Fswig-3.0.12%2Fswig-3.0.12.tar.gz%2Fdownload

# extract and configure
#RUN cd /opt; tar xf /tmp/swig-3.0.12.tar.gz; /tmp/swig-3.0.12.tar.gz; cd swig-3.0.12;  ./configure --prefix=/usr ;  make -j 4; make install; cp swig /usr/local/bin

# snowboy
#RUN pip install paho-mqtt
#RUN cd /opt; git clone https://github.com/Kitt-AI/snowboy.git; cd snowboy; python setup.py install;  cd swig/Python; make; 
#cp snowboydetect.py /opt/rasa/anaconda/lib/python2.7/ ; 
#RUN  cd /opt/snowboy ; python setup.py install;
#RUN cp _snowboydetect.so /opt/rasa/anaconda/lib/

#RUN mkdir -p /opt/snips_hotword_snowboy ; cp /opt/snowboy/swig/Python/* /opt/snips_hotword_snowboy/




#ENTRYPOINT ["/opt/snips/snips-entrypoint.sh"]

#CMD [""]


