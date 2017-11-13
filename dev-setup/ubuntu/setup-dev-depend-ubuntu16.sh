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
#!/bin/bash

echo 'Adding repositories and keys...'
echo "deb http://us.archive.ubuntu.com/ubuntu xenial main universe" | sudo tee -a /etc/apt/sources.list

sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 68DB5E88
echo "deb https://repo.sovrin.org/deb xenial stable" | sudo tee -a /etc/apt/sources.list

sudo apt-get update

echo 'Added repositories and keys'


echo 'Installing libsodium...'
sudo apt-get install libsodium18
echo 'Installed libsodium'


echo 'Installing Charm Crypto...'
sudo apt-get install python3-charm-crypto
echo 'Installed Charm Crypto'


echo 'Installing Libindy Crypto...'
sudo apt-get install libindy-crypto
echo 'Installed Libindy Crypto'

