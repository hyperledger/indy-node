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
# Update repository signing keys
# --------------------------------------------------------------------------------------------------------
# Hyperledger
RUN gpg --keyserver keyserver.ubuntu.com --recv-keys 9692C00E657DDE61 && \
    gpg --export 9692C00E657DDE61 > /etc/apt/keyrings/hyperledger.gpg
# ========================================================================================================

# Plenum
#  - https://github.com/hyperledger/indy-plenum/issues/1546
#  - Needed to pick up rocksdb=5.8.8
RUN echo "deb [signed-by=/etc/apt/keyrings/hyperledger.gpg] https://hyperledger.jfrog.io/artifactory/indy jammy dev rc stable" > /etc/apt/sources.list.d/hyperledger.list

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
    pyzmq==26.2.1

# install fpm
RUN gem install --no-document rake dotenv:2.8.1 fpm:1.14.2

RUN apt -y autoremove \
    && rm -rf /var/lib/apt/lists/*

