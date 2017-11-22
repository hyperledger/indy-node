FROM hyperledger/indy-baseimage
LABEL maintainer="Andrey Kononykhin andkononykhin@gmail.com"

# sovrin repos
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 68DB5E88 && \
    echo "deb https://repo.sovrin.org/deb xenial master" >> /etc/apt/sources.list && \
    apt-get update

COPY scripts/user.sh /usr/local/bin/indy_ci_add_user
COPY scripts/charm_crypto.sh /usr/local/bin/indy_ci_charm_crypto
RUN bash -c "chmod 755 /usr/local/bin/indy_ci_{add_user,charm_crypto}"

RUN indy_image_clean
