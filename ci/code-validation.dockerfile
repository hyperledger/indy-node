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
	pip \ 
	setuptools \
	pep8 \
	pep8-naming \
	flake8
