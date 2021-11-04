FROM ubuntu:16.04
LABEL maintainer="Hyperledger <hyperledger-indy@lists.hyperledger.org>"

RUN apt-get update && apt-get dist-upgrade -y

# very common packages
RUN apt-get update && apt-get install -y \
    git \
    wget \
    vim \
    apt-transport-https \
    ca-certificates \
    apt-utils

# python
RUN apt-get update && apt-get install -y \
    python3.5 \
    python3-pip \
    python-setuptools
    
# pypi based packages
RUN pip3 install -U\
    "pip <10.0.0" \
    "setuptools<=50.3.2"

# needs to be installed separately and pinned to version 20.0.25 to be compatible with Python3.5 and packages like zipp==1.2.0
RUN pip3 install -U \
    'virtualenv==20.0.35'


RUN ln -s /usr/bin/pip3 /usr/bin/pip

COPY scripts/clean.sh /usr/local/bin/indy_image_clean
RUN chmod 755 /usr/local/bin/indy_image_clean

COPY __VERSION_FILE__ /

RUN indy_image_clean
