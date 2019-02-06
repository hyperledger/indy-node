#!/usr/bin/env bash

# dirs to be created
node_dirs="/etc/indy /var/lib/indy /var/log/indy"

# create dirs
for dr in $node_dirs
do
    sudo mkdir -p $dr
done

# generate base config if not exists
if [ ! -f /etc/indy/indy_config.py ]; then
    echo "NETWORK_NAME = 'sandbox'" | sudo tee -a /etc/indy/indy_config.py

    echo "LEDGER_DIR = '/var/lib/indy'" | sudo tee -a /etc/indy/indy_config.py
    echo "LOG_DIR = '/var/log/indy'"  | sudo tee -a /etc/indy/indy_config.py
    echo "KEYS_DIR = '/var/lib/indy'"  | sudo tee -a /etc/indy/indy_config.py
    echo "GENESIS_DIR = '/var/lib/indy'" | sudo tee -a /etc/indy/indy_config.py
    echo "BACKUP_DIR = '/var/lib/indy/backup'" | sudo tee -a /etc/indy/indy_config.py
    echo "PLUGINS_DIR = '/var/lib/indy/plugins'" | sudo tee -a /etc/indy/indy_config.py
    echo "NODE_INFO_DIR = '/var/lib/indy'" | sudo tee -a /etc/indy/indy_config.py
fi

# grant permissions
for dr in $node_dirs
do
    sudo chown -R ${USER}:${USER} $dr
    sudo chmod -R ug+rwx $dr
done
