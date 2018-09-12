FROM hyperledger/indy-core-baseci:0.0.1
LABEL maintainer="Hyperledger <hyperledger-indy@lists.hyperledger.org>"

ARG uid=1000
ARG user=indy
ARG venv=venv

RUN apt-get update -y && apt-get install -y \
    python3-nacl \
    libindy-crypto=0.4.3 \
    libindy=1.6.1~683 \
# rocksdb python wrapper
    libbz2-dev \
    zlib1g-dev \
    liblz4-dev \
    libsnappy-dev \
    rocksdb=5.8.8

RUN indy_ci_add_user $uid $user $venv && \
    indy_ci_charm_crypto $user $venv

RUN indy_image_clean

USER $user
WORKDIR /home/$user
