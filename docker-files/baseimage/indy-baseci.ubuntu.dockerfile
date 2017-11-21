FROM hyperledger/indy-baseimage
LABEL maintainer="Andrey Kononykhin andkononykhin@gmail.com"

COPY scripts/user.sh /usr/local/bin/indy_ci_add_user
COPY scripts/charm_crypto.sh /usr/local/bin/indy_ci_charm_crypto
COPY scripts/libindy.sh /usr/local/bin/indy_ci_libindy
RUN chmod 755 /usr/local/bin/indy_ci_*
