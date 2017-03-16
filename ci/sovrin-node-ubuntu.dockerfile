# Development
FROM ubuntu:16.04

# Install environment
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys D82D8E35
RUN echo "deb https://repo.evernym.com/deb xenial master" >> /etc/apt/sources.list
RUN apt-get update -y
RUN apt-get install -y \ 
	git \
	wget \
	python3.5 \
	python3-pip \
	python-setuptools \
	python3-nacl \
	python3-charm-crypto
RUN pip3 install -U \ 
	pip \ 
	setuptools \
	virtualenv
RUN apt-get update -y
RUN apt-get install -y \ 
	python3-charm-crypto
RUN useradd -ms /bin/bash sovrin
USER sovrin
WORKDIR /home/sovrin