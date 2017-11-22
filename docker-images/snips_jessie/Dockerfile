FROM debian:jessie
MAINTAINER Steve Ryan <stever@syntithenai.com>

# system dependancies
RUN  export DEBIAN_FRONTEND="noninteractive" ; apt-get  --allow-unauthenticated update && apt-get -f install && apt-get install  -fyq  --force-yes   virtualenv python-pip python-sklearn python-dev libpng12-0 libpng12-dev  libfreetype6 libfreetype6-dev nano apt-transport-https wget dirmngr nano bzip2 git
#  && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*;

RUN bash -c  'echo "deb https://debian.snips.ai/$(lsb_release -cs) stable main" > /etc/apt/sources.list.d/snips.list'
RUN apt-key adv --keyserver pgp.mit.edu --recv-keys F727C778CCB0A455

RUN apt-get update
RUN apt-get install -y snips-platform-voice
