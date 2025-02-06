# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/main/containers/ubuntu/.devcontainer/base.Dockerfile

# [Choice] Ubuntu version (use ubuntu-22.04 or ubuntu-18.04 on local arm64/Apple Silicon): ubuntu-22.04, ubuntu-20.04, ubuntu-18.04
ARG VARIANT="ubuntu-22.04"
FROM mcr.microsoft.com/vscode/devcontainers/base:${VARIANT}

RUN apt-get update -y && apt-get install -y \
    # common stuff
    git \
    wget \
    gnupg \
    apt-transport-https \
    ca-certificates \
    apt-utils \
    curl \
    jq

# ========================================================================================================
# Get repository signing keys
# --------------------------------------------------------------------------------------------------------
# Hyperledger
RUN gpg --keyserver keyserver.ubuntu.com --recv-keys 9692C00E657DDE61 && \
    gpg --export 9692C00E657DDE61 > /etc/apt/trusted.gpg.d/hyperledger.gpg
# ========================================================================================================

# Plenum
#  - https://github.com/hyperledger/indy-plenum/issues/1546
#  - Needed to pick up rocksdb=5.8.8
RUN echo "deb [signed-by=/etc/apt/trusted.gpg.d/hyperledger.gpg] https://hyperledger.jfrog.io/artifactory/indy jammy dev rc" > /etc/apt/sources.list.d/hyperledger.list

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
    # Indy SDK is not used anymore
    #libindy \
    libssl3 

RUN pip3 install -U \
    # Required by setup.py
    setuptools==75.8.0 \
    pyzmq==26.2.1 \
    Cython==0.29.36

# install fpm
RUN gem install --no-document rake dotenv:2.8.1 fpm:1.14.2

RUN apt -y autoremove \
    && rm -rf /var/lib/apt/lists/*
