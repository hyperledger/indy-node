FROM indybase

ARG uid=1000

# Install environment
RUN apt-get update -y && apt-get install -y \ 
	git \
	wget \
	python3.5 \
	python3-pip \
	python-setuptools \
	python3-nacl \
	apt-transport-https \
	ca-certificates 
RUN pip3 install -U \ 
	'pip<10.0.0' \
	setuptools
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 68DB5E88
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys BD33704C
RUN echo "deb https://repo.sovrin.org/deb xenial master" >> /etc/apt/sources.list
RUN echo "deb https://repo.sovrin.org/sdk/deb xenial master" >> /etc/apt/sources.list
RUN useradd -ms /bin/bash -l -u $uid indy
RUN apt-get update -y && apt-get install -y python3-indy-crypto=0.4.1 indy-plenum=1.5.484 indy-node=1.5.536 sovrin=1.1.63
# RUN pip3 install python3-indy
USER indy
WORKDIR /home/indy
