# Development
FROM ubuntu:16.04

# Install environment
RUN apt-get update -y
RUN apt-get install -y \ 
	git \
	wget \
	python3.5 \
	python3-pip \
	python-setuptools \
	python3-nacl \
	python-software-properties \
	apt-transport-https \
  ca-certificates
RUN pip3 install -U \ 
	pip \ 
	setuptools \
	virtualenv
RUN 
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys D82D8E35
RUN add-apt-repository "deb https://repo.evernym.com/deb xenial stable"
RUN apt-get update -y
RUN apt-get install -y \ 
	python3-charm-crypto
RUN useradd -ms /bin/bash sovrin
USER sovrin
WORKDIR /home/sovrin