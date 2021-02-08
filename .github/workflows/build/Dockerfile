FROM hyperledger/indy-core-baseci:0.0.3-master
LABEL maintainer="Hyperledger <hyperledger-indy@lists.hyperledger.org>"

RUN apt-get update -y && apt-get install -y \
    python3-nacl \
    libindy-crypto=0.4.5 \
    libindy=1.13.0~1420 \
# rocksdb python wrapper
    libbz2-dev \
    zlib1g-dev \
    liblz4-dev \
    libsnappy-dev \
    rocksdb=5.8.8 \
    ursa=0.3.2-2 \
    jq

RUN indy_image_clean
