FROM __NS__/indy-baseci:0.0.3-master
LABEL maintainer="Hyperledger <hyperledger-indy@lists.hyperledger.org>"

# indy repos
RUN echo "deb https://repo.sovrin.org/sdk/deb xenial master" >> /etc/apt/sources.list && \
    apt-get update

# set highest priority for indy sdk packages in core repo
COPY indy-core-repo.preferences /etc/apt/preferences.d/indy-core-repo

COPY __VERSION_FILE__ /

RUN indy_image_clean
