# Development
FROM ubuntu:18.04
LABEL maintainer="Hyperledger <hyperledger-indy@lists.hyperledger.org>"

RUN apt-get update && apt-get dist-upgrade -y

# Install environment
RUN apt-get install -y \
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
