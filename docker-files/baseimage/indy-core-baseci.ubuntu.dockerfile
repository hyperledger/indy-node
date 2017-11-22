FROM hyperledger/indy-baseci
LABEL maintainer="Andrey Kononykhin andkononykhin@gmail.com"

# sovrin repos
RUN echo "deb https://repo.sovrin.org/sdk/deb xenial master" >> /etc/apt/sources.list && \
    apt-get update

# set highest priority for indy sdk packages in core repo
COPY indy-core-repo.preferences /etc/apt/preferences.d/indy-core-repo
COPY scripts/libindy.sh /usr/local/bin/indy_ci_libindy
RUN chmod 755 /usr/local/bin/indy_ci_libindy

RUN indy_image_clean
