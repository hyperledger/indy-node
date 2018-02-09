FROM indybase

#ARG indyVersion=1.1.26
ARG uid=1000
ARG gid=0

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
	pip \ 
	setuptools

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 68DB5E88
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys BD33704C

RUN echo "deb https://repo.evernym.com/deb xenial stable" >> /etc/apt/sources.list
RUN echo "deb https://repo.sovrin.org/deb xenial stable" >> /etc/apt/sources.list

RUN useradd -ms /bin/bash -l -u $uid -G $gid indy
RUN apt-get update -y && apt-get install -y indy-node