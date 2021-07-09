FROM ubuntu:20.04

RUN apt-get update -y && apt-get install -y \
        apt-transport-https \
        ca-certificates

RUN apt-get update -y && apt-get install -y \
    # common stuff
        git \
        wget \
        unzip \
        python3-pip \
        python3-venv \
    # fpm
        ruby \
        ruby-dev \
        rubygems \
        gcc \
        make \
    # Just for testing (libsodium23 and iptables)
        libsodium23 \
        iptables \
        at \
    # rocksdb python wrapper
        libbz2-dev \
        zlib1g-dev \
        liblz4-dev \
        libsnappy-dev \
        libzstd-dev \
    && rm -rf /var/lib/apt/lists/*

# issues with pip>=10:
# https://github.com/pypa/pip/issues/5240
# https://github.com/pypa/pip/issues/5221

#setuptools v52.0.0 fails, because easy_install was removed https://setuptools.readthedocs.io/en/latest/history.html#v52-0-0
RUN python3 -m pip install -U pip setuptools==50.3.2
    # \ && pip3 list

# install fpm
RUN gem install --no-document rake fpm

WORKDIR /root

ADD . /root
