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
	apt-transport-https \
	ca-certificates
RUN pip3 install -U \ 
	pip \ 
	setuptools \
	virtualenv
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EAA542E8
RUN echo "deb https://repo.evernym.com/deb xenial master" >> /etc/apt/sources.list
RUN apt-get update -y
RUN apt-get install -y \ 
	python3-charm-crypto
RUN useradd -ms /bin/bash sovrin
USER sovrin
RUN cd /home/sovrin && virtualenv -p python3.5 test
USER root
RUN ln -sf /home/sovrin/test/bin/python /usr/local/bin/python
USER sovrin
WORKDIR /home/sovrin