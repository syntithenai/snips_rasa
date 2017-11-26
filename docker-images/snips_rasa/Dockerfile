FROM snipsdocker/platform:x86-latest
MAINTAINER Steve Ryan <stever@syntithenai.com>

# system dependancies
RUN  export DEBIAN_FRONTEND="noninteractive" ; apt-get  --allow-unauthenticated update && apt-get -f install && apt-get install  -fyq  --force-yes   virtualenv python-pip python-sklearn python-dev libpng12-0 libpng12-dev  libfreetype6 libfreetype6-dev nano apt-transport-https wget
#  && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*;

# Download and install Anaconda
# ARM
#RUN mkdir /opt/rasa  &&  export HOME=/opt/rasa/ && export ANACONDA_REPO='http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-armv7l.sh' && export ANACONDA_INSTALLER='Miniconda3-latest-Linux-armv7l.sh' && wget -P /tmp/ $ANACONDA_REPO  && bash "/tmp/$ANACONDA_INSTALLER" -b -p $HOME/anaconda &&  export PATH="$HOME/anaconda/bin:$PATH" &&  echo 'export PATH="$HOME/anaconda/bin:$PATH"' >> ~/.bash_profile &&  echo 'export PATH="~/anaconda/bin:$PATH"' >> ~/.bashrc
# X86
RUN mkdir /opt/rasa  &&  export HOME=/opt/rasa/ && export ANACONDA_REPO='http://repo.continuum.io/miniconda/Miniconda2-4.3.30-Linux-x86_64.sh' && export ANACONDA_INSTALLER='Miniconda2-4.3.30-Linux-x86_64.sh' && wget -P /tmp/ $ANACONDA_REPO  && bash "/tmp/$ANACONDA_INSTALLER" -b -p $HOME/anaconda &&  export PATH="$HOME/anaconda/bin:$PATH" &&  echo 'export PATH="$HOME/anaconda/bin:$PATH"' >> ~/.bash_profile &&  echo 'export PATH="~/anaconda/bin:$PATH"' >> ~/.bashrc

# scikit sklearn
RUN /opt/rasa/anaconda/bin/conda install scikit-learn 
RUN /opt/rasa/anaconda/bin/pip install -U sklearn-crfsuite

# install rasa_nlu and requirementS
RUN /opt/rasa/anaconda/bin/pip install setuptools ; echo "done" 
RUN /opt/rasa/anaconda/bin/pip install -U spacy ; echo "done" 
RUN /opt/rasa/anaconda/bin/python -m spacy download en ; echo "done" 
RUN /opt/rasa/anaconda/bin/pip install -U scikit-learn scipy sklearn-crfsuite  paho-mqtt ; echo "done" 
RUN apt-get install -y git
RUN cd /opt/rasa && git clone https://github.com/RasaHQ/rasa_nlu.git && cd rasa_nlu && /opt/rasa/anaconda/bin/pip install -r requirements.txt;  echo done;
RUN cd /opt/rasa/rasa_nlu && /opt/rasa/anaconda/bin/python setup.py install ; echo "done" 

# rasa core
RUN cd /opt/rasa && git clone https://github.com/RasaHQ/rasa_core.git 
RUN cd /opt/rasa/rasa_core && /opt/rasa/anaconda/bin/pip install -r requirements.txt 
RUN cd /opt/rasa/rasa_core && /opt/rasa/anaconda/bin/pip install -e .

RUN /opt/rasa/anaconda/bin/pip install -U docker-compose ; echo "done" 
RUN /opt/rasa/anaconda/bin/pip install -U setuptools ; echo "done" 

# and again to force ??
RUN /opt/rasa/anaconda/bin/pip install -U spacy ; echo "done" 
RUN /opt/rasa/anaconda/bin/python -m spacy download en ; echo "done" 
RUN /opt/rasa/anaconda/bin/pip install -U Flask ; echo "done" 

# raspi
#RUN apt-get install -y oracle-java7-jdk
# intel
RUN apt-get install -y openjdk-7-jdk


RUN /opt/rasa/anaconda/bin/pip install duckling



# hacked entrypoint script and ENV VAR to trigger rasa
#COPY ./snips-entrypoint.sh /opt/snips/snips-entrypoint.sh
#ENV USE_RASA_NLU 1

# SNOWBOY / RECENT SWIG * using python2 rather than anaconda python3
RUN apt-get install  -fyq  --force-yes  wget swig3.0 python-pyaudio python3-pyaudio sox libatlas-base-dev libpcre3-dev python-pip git python-dev portaudio19-dev psutils pulseaudio
RUN pip install pyaudio
#apt-get install libportaudio2 libportaudiocpp0 python-pyaudio python-dev

# download swig 3.0.12
RUN wget -O /tmp/swig-3.0.12.tar.gz https://downloads.sourceforge.net/project/swig/swig/swig-3.0.12/swig-3.0.12.tar.gz?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fswig%2Ffiles%2Fswig%2Fswig-3.0.12%2Fswig-3.0.12.tar.gz%2Fdownload

# extract and configure
RUN cd /opt; tar xf /tmp/swig-3.0.12.tar.gz; cd swig-3.0.12;  ./configure --prefix=/usr ;  make -j 4; make install; cp swig /usr/local/bin

# snowboy
RUN cd /opt; git clone https://github.com/Kitt-AI/snowboy.git; cd snowboy; python setup.py install;  cd swig/Python; make; 
#cp snowboydetect.py /opt/rasa/anaconda/lib/python2.7/ ; 
RUN  cd /opt/snowboy ; /opt/rasa/anaconda/bin/python setup.py install;
#RUN cp _snowboydetect.so /opt/rasa/anaconda/lib/

RUN mkdir -p /opt/snips_hotword_snowboy ; cp /opt/snowboy/swig/Python/* /opt/snips_hotword_snowboy/

#ENV PULSE_SERVER=192.168.1.100



#RUN touch /tmp/pulse-socket; chmod 777 /tmp/pulse-socket

#RUN addgroup --system --group pulse && \
#    adduser --system --group pulse && \
#    addgroup pulse audio && \
#    mkdir /tmp/pulse && \
#    chown -R pulse:pulse /home/pulse /tmp/pulse
 
RUN mkdir -p /var/run/pulse; chmod 777 /var/run/pulse
    
#COPY ./asound.conf /etc/asound.conf

CMD ["/opt/snips/snips-entrypoint.sh"]
