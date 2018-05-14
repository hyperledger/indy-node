# Development
FROM ubuntu:16.04

ARG uid=1000

# Install environment
RUN apt-get update -y && apt-get install -y \
	git \
	wget \
	python3.5 \
	python3-pip \
	python-setuptools \
	python3-nacl
RUN pip3 install -U \ 
	'pip<10.0.0' \
	setuptools \
	pep8==1.7.1 \
	pep8-naming==0.6.1 \
	flake8==3.5.0
