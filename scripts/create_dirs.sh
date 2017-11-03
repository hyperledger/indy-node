#!/usr/bin/env bash

if [ "${SUDO_USER}" == "" ]; then
    echo "It should be run with sudo"
    exit
fi

# dirs to be created
node_dirs="/etc/indy /var/lib/indy /var/log/indy /home/${SUDO_USER}/.indy-cli"

# create dirs
for dr in $node_dirs
do
    mkdir -p $dr
done

# generate base config if not exists
if [ ! -f /etc/indy/indy_config.py ]; then
    echo "NETWORK_NAME = 'sandbox'" > /etc/indy/indy_config.py

    echo "baseDir = '/var/lib/indy'" >> /etc/indy/indy_config.py
    echo "NODE_BASE_DATA_DIR = baseDir" >> /etc/indy/indy_config.py
    echo "CLI_BASE_DIR = '~/.indy-cli/'" >> /etc/indy/indy_config.py
    echo "CLI_NETWORK_DIR = '~/.indy-cli/networks'" >> /etc/indy/indy_config.py
    echo "LOG_DIR = '/var/log/indy'" >> /etc/indy/indy_config.py
fi

# grant permissions
for dr in $node_dirs
do
    chown -R ${SUDO_USER}:${SUDO_USER} $dr
    chmod -R ug+rwx $dr
done
