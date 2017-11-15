#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#!/usr/bin/env bash

# dirs to be created
node_dirs="/etc/indy /var/lib/indy /var/log/indy /home/${USER}/.indy-cli"

# create dirs
for dr in $node_dirs
do
    sudo mkdir -p $dr
done

# generate base config if not exists
if [ ! -f /etc/indy/indy_config.py ]; then
    echo "NETWORK_NAME = 'sandbox'" | sudo tee -a /etc/indy/indy_config.py

    echo "baseDir = '/var/lib/indy'" | sudo tee -a /etc/indy/indy_config.py
    echo "NODE_BASE_DATA_DIR = baseDir" | sudo tee -a /etc/indy/indy_config.py
    echo "CLI_BASE_DIR = '~/.indy-cli/'" | sudo tee -a /etc/indy/indy_config.py
    echo "CLI_NETWORK_DIR = '~/.indy-cli/networks'" | sudo tee -a /etc/indy/indy_config.py
    echo "LOG_DIR = '/var/log/indy'" | sudo tee -a /etc/indy/indy_config.py
fi

# grant permissions
for dr in $node_dirs
do
    sudo chown -R ${USER}:${USER} $dr
    sudo chmod -R ug+rwx $dr
done
