# Development
FROM ubuntu:16.04

ARG uid=1000

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
RUN useradd -ms /bin/bash -u $uid sovrin
USER sovrin
RUN virtualenv -p python3.5 /home/sovrin/test
RUN cp -r /usr/local/lib/python3.5/dist-packages/Charm_Crypto-0.0.0.egg-info /home/sovrin/test/lib/python3.5/site-packages/Charm_Crypto-0.0.0.egg-info
RUN cp -r /usr/local/lib/python3.5/dist-packages/charm /home/sovrin/test/lib/python3.5/site-packages/charm
RUN mkdir /home/sovrin/.sovrin
RUN echo "OrientDB = {\"user\": \"root\",\"password\": \"password\",\"host\": \"127.0.0.1\",\"port\": 2424}" >> /home/sovrin/.sovrin/sovrin_config.py
USER root
RUN ln -sf /home/sovrin/test/bin/python /usr/local/bin/python
RUN ln -sf /home/sovrin/test/bin/pip /usr/local/bin/pip
USER sovrin
WORKDIR /home/sovrin