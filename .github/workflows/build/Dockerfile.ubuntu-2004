FROM ubuntu:20.04

ARG uid=1000
ARG user=indy

RUN apt-get update -y && apt-get install -y \
    # common stuff
    git \
    wget \
    gnupg \
    apt-transport-https \
    ca-certificates \
    apt-utils

# ========================================================================================================
# Update repository signing keys
# --------------------------------------------------------------------------------------------------------
# Hyperledger
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 9692C00E657DDE61 && \
    # Sovrin
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88
# ========================================================================================================

# Plenum
#  - https://github.com/hyperledger/indy-plenum/issues/1546
#  - Needed to pick up rocksdb=5.8.8
RUN echo "deb  https://hyperledger.jfrog.io/artifactory/indy focal dev"  >> /etc/apt/sources.list && \
    echo "deb http://security.ubuntu.com/ubuntu bionic-security main"  >> /etc/apt/sources.list && \
    echo "deb https://repo.sovrin.org/deb bionic master" >> /etc/apt/sources.list && \
    echo "deb https://repo.sovrin.org/sdk/deb bionic master" >> /etc/apt/sources.list

# Sovrin
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88 

RUN apt-get update -y && apt-get install -y \
    # Python
    python3-pip \
    python3-nacl \
    # rocksdb python wrapper
    rocksdb=5.8.8 \
    libgflags-dev \
    libsnappy-dev \
    zlib1g-dev \
    libbz2-dev \
    liblz4-dev \
    libgflags-dev \
    # zstd is needed for caching in github actions pipeline
    zstd \
    # fpm
    ruby \
    ruby-dev \
    rubygems \
    gcc \
    make \
    # Indy Node and Plenum
    libssl1.0.0 \
    ursa=0.3.2-1 \
    # Indy SDK
    libindy=1.15.0~1625-bionic \
    # Need to move libursa.so to parent dir
    && mv /usr/lib/ursa/* /usr/lib && rm -rf /usr/lib/ursa

RUN pip3 install -U \
    # Required by setup.py
    setuptools==50.3.2 \
    # Still pinned. Needs to be update like in plenum
    'pip<10.0.0' \
    'pyzmq==18.1.0'


# install fpm
RUN gem install --no-document rake fpm

RUN apt-get -y autoremove \
    && rm -rf /var/lib/apt/lists/*
