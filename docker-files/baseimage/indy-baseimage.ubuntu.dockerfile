FROM ubuntu:16.04
LABEL maintainer="Andrey Kononykhin andkononykhin@gmail.com"

# TODO enable for dockerhub publishing
#RUN apt-get update && apt-get dist-upgrade -y

# very common packages
RUN apt-get update -y && apt-get install -y \
    git \
    wget \
    vim \
    apt-transport-https \
    ca-certificates \
    apt-utils

# sovrin repo
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 68DB5E88 && \
    echo "deb https://repo.sovrin.org/deb xenial master" >> /etc/apt/sources.list \
    echo "deb https://repo.sovrin.org/sdk/deb xenial master" >> /etc/apt/sources.list

# python
RUN apt-get update -y && apt-get install -y \
    python3.5 \
    python3-pip \
    python-setuptools
    
# pypi base packages
RUN pip3 install -U \ 
    pip \ 
    setuptools \
    virtualenv

COPY scripts/clean.sh /usr/local/bin/indy_image_clean
RUN chmod 755 /usr/local/bin/indy_image_clean
RUN indy_image_clean
