FROM hyperledger/indy-baseci
LABEL maintainer="Hyperledger <hyperledger-indy@lists.hyperledger.org>"

# sovrin repos
RUN echo "deb https://repo.sovrin.org/sdk/deb xenial master" >> /etc/apt/sources.list && \
    apt-get update

# set highest priority for indy sdk packages in core repo
COPY indy-core-repo.preferences /etc/apt/preferences.d/indy-core-repo

RUN indy_image_clean
