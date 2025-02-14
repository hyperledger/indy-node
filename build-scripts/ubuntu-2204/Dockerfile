FROM ubuntu:22.04

ARG uid=1000
ARG user=indy

RUN apt update -y && apt install -y \
    # common stuff
    git \
    wget \
    gnupg \
    apt-transport-https \
    ca-certificates \
    apt-utils

# ========================================================================================================
# Get repository signing keys
# --------------------------------------------------------------------------------------------------------
# Hyperledger
RUN gpg --keyserver keyserver.ubuntu.com --recv-keys 9692C00E657DDE61 && \
    gpg --export 9692C00E657DDE61 > /etc/apt/keyrings/hyperledger.gpg

# todo: Will be removed when libindy will have been replace by indy-vdr, askar, and indy-credx
# bionic key
RUN gpg --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32 && \
    gpg --export 3B4FE6ACC0B21F32 > /etc/apt/keyrings/ubuntu-bionic.gpg
# sovrin key
RUN gpg --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88 && \
    gpg --export CE7709D068DB5E88 > /etc/apt/keyrings/sovrin.gpg
# ========================================================================================================

# Plenum
#  - https://github.com/hyperledger/indy-plenum/issues/1546
#  - Needed to pick up rocksdb=5.8.8
RUN echo "deb [signed-by=/etc/apt/keyrings/hyperledger.gpg] https://hyperledger.jfrog.io/artifactory/indy jammy dev rc" > /etc/apt/sources.list.d/hyperledger.list

# todo: Will be removed when libindy will have been replace by indy-vdr, askar, and indy-credx
RUN echo "deb [signed-by=/etc/apt/keyrings/ubuntu-bionic.gpg] http://security.ubuntu.com/ubuntu bionic-security main" > /etc/apt/sources.list.d/ubuntu-bionic.list
RUN echo "deb [signed-by=/etc/apt/keyrings/sovrin.gpg] https://repo.sovrin.org/deb bionic master" > /etc/apt/sources.list.d/sovrin.list
RUN echo "deb [signed-by=/etc/apt/keyrings/sovrin.gpg] https://repo.sovrin.org/sdk/deb bionic master" >> /etc/apt/sources.list.d/sovrin.list


RUN apt update -y && apt install -y \
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
    libssl3 
# Indy Node and Plenum
# Indy SDK is not used anymore
#libindy \
# rsa=0.3.2-1 \
# Indy SDK
# libindy=1.15.0~1625-bionic \
# Need to move libursa.so to parent dir
# && mv /usr/lib/ursa/* /usr/lib && rm -rf /usr/lib/ursa

RUN pip3 install -U \
    # Required by setup.py
    setuptools==75.8.0 \
    pyzmq==22.3.0

# install fpm
RUN gem install --no-document rake dotenv:2.8.1 fpm:1.15.0 && \
    pip3 install Cython==0.29.36

RUN apt -y autoremove \
    && rm -rf /var/lib/apt/lists/*

