FROM gitpod/workspace-base:2024-09-11-00-04-27 as base

USER gitpod


RUN sudo apt-get update -y && sudo apt-get install -y \
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
# Update repository signing keys
# --------------------------------------------------------------------------------------------------------
# Hyperledger
RUN sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 9692C00E657DDE61 && \
    # Sovrin
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88
# ========================================================================================================

# Plenum
#  - https://github.com/hyperledger/indy-plenum/issues/1546
#  - Needed to pick up rocksdb=5.8.8
RUN sudo add-apt-repository 'deb  https://hyperledger.jfrog.io/artifactory/indy focal dev' && \
    sudo add-apt-repository 'deb http://security.ubuntu.com/ubuntu bionic-security main' && \
    sudo add-apt-repository 'deb https://repo.sovrin.org/deb bionic master'  && \
    sudo add-apt-repository 'deb https://repo.sovrin.org/sdk/deb bionic master'



RUN sudo apt-get update -y && sudo apt-get install -y \
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
    && sudo mv /usr/lib/ursa/* /usr/lib && sudo rm -rf /usr/lib/ursa

RUN pip3 install -U \
    # Required by setup.py
    setuptools==50.3.2 \
    'pyzmq==22.3.0'


# install fpm
RUN sudo gem install --no-document rake dotenv:2.8.1 fpm:1.14.2