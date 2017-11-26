FROM syntithenai/snips_base
MAINTAINER Steve Ryan <stever@syntithenai.com>


# system dependancies
RUN  export DEBIAN_FRONTEND="noninteractive" ; apt-get  --allow-unauthenticated update && apt-get -f install && apt-get install  -fyq  --force-yes   virtualenv python-pip python-sklearn python-dev nano apt-transport-https wget dirmngr nano bzip2 git lsb-release supervisor 

# libpng12-0 libpng12-dev  libfreetype6 libfreetype6-dev 
#  && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*;

RUN export DEBIAN_FRONTEND="noninteractive" ;  apt-get -f install && apt-get install  -fyq  --force-yes init-system-helpers

# SWITCH ON ARCHITECTURE TO SELECT APT SOURCES
RUN if [ `uname -m` = "armv7l" ]; then  bash -c  'echo "deb https://raspbian.snips.ai/$(lsb_release -cs) stable main" > /etc/apt/sources.list.d/snips.list'; apt-key adv --keyserver pgp.mit.edu --recv-keys D4F50CDCA10A2849; elif [ `uname -m` = "x86_64" ]; then bash -c  'echo "deb https://debian.snips.ai/$(lsb_release -cs) stable main" > /etc/apt/sources.list.d/snips.list'; apt-key adv --keyserver pgp.mit.edu --recv-keys F727C778CCB0A455; fi

RUN apt-get update 
RUN apt-get install -y snips-platform-voice pulseaudio jq snips-watch


# startup script from docker image using supervisord
COPY snips-entrypoint.sh /opt/snips/snips-entrypoint.sh
# default config file
COPY snips.toml /etc/snips.toml
# sample music assistant
COPY assistant /usr/share/snips/assistant
# not present after installation so copied from docker image
COPY snips-tts /usr/bin/snips-tts

# DONE SNIPS 

# SNOWBOY / RECENT SWIG * using default python rather than anaconda 
RUN apt-get install  -fyq  --force-yes  wget swig3.0 python-pyaudio python3-pyaudio sox python-pip git python-dev psutils pulseaudio libpcre3-dev portaudio19-dev
# libatlas-base-dev 
RUN pip install pyaudio
#apt-get install libportaudio2 libportaudiocpp0 python-pyaudio python-dev

# download swig 3.0.12
RUN wget -O /tmp/swig-3.0.12.tar.gz https://downloads.sourceforge.net/project/swig/swig/swig-3.0.12/swig-3.0.12.tar.gz?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fswig%2Ffiles%2Fswig%2Fswig-3.0.12%2Fswig-3.0.12.tar.gz%2Fdownload

# extract and configure
RUN cd /opt; tar xf /tmp/swig-3.0.12.tar.gz; cd swig-3.0.12;  ./configure --prefix=/usr ;  make -j 4; make install; cp swig /usr/local/bin

# snowboy
RUN cd /opt; git clone https://github.com/Kitt-AI/snowboy.git; cd snowboy; python setup.py install;  cd swig/Python; make; 
#cp snowboydetect.py /opt/rasa/anaconda/lib/python2.7/ ; 
RUN  cd /opt/snowboy ; python setup.py install;
#RUN cp _snowboydetect.so /opt/rasa/anaconda/lib/

RUN mkdir -p /opt/snips_hotword_snowboy ; cp /opt/snowboy/swig/Python/* /opt/snips_hotword_snowboy/


# RASA

# USE (MORE EFFICIENT) ORACLE JDK FOR RASPI
RUN if [ `uname -m` = "armv7l" ]; then  apt-get install -y oracle-java7-jdk; elif [ `uname -m` = "x86_64" ]; then apt-get install -y openjdk-7-jdk; fi

# Download and install Anaconda
# SWITCH ON ARCHITECTURE TO SELECT SOURCES
RUN if [ `uname -m` = "armv7l" ]; then  mkdir /opt/rasa  &&  export HOME=/opt/rasa/ && export ANACONDA_REPO='http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-armv7l.sh' && export ANACONDA_INSTALLER='Miniconda3-latest-Linux-armv7l.sh' && wget -P /tmp/ $ANACONDA_REPO  && bash "/tmp/$ANACONDA_INSTALLER" -b -p $HOME/anaconda &&  export PATH="$HOME/anaconda/bin:$PATH" &&  echo 'export PATH="$HOME/anaconda/bin:$PATH"' >> ~/.bash_profile &&  echo 'export PATH="~/anaconda/bin:$PATH"' >> ~/.bashrc; elif [ `uname -m` = "x86_64" ]; then mkdir /opt/rasa  &&  export HOME=/opt/rasa/ && export ANACONDA_REPO='http://repo.continuum.io/miniconda/Miniconda2-4.3.30-Linux-x86_64.sh' && export ANACONDA_INSTALLER='Miniconda2-4.3.30-Linux-x86_64.sh' && wget -P /tmp/ $ANACONDA_REPO  && bash "/tmp/$ANACONDA_INSTALLER" -b -p $HOME/anaconda &&  export PATH="$HOME/anaconda/bin:$PATH" &&  echo 'export PATH="$HOME/anaconda/bin:$PATH"' >> ~/.bash_profile &&  echo 'export PATH="~/anaconda/bin:$PATH"' >> ~/.bashrc; fi

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
RUN /opt/rasa/anaconda/bin/pip install duckling


ENTRYPOINT ["/opt/snips/snips-entrypoint.sh"]

CMD [""]


