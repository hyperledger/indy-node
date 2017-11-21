FROM hyperledger/indy-baseci
LABEL maintainer="Andrey Kononykhin andkononykhin@gmail.com"

ARG uid=1000
ARG user=indy
ARG venv=venv

RUN apt-get update -y && apt-get install -y \
    python3-nacl \
    libindy-crypto=0.1.6

RUN indy_ci_add_user $uid $user $venv && \
    indy_ci_libindy $user && \
    indy_ci_charm_crypto $user $venv

RUN indy_image_clean

USER $user
WORKDIR /home/$user
