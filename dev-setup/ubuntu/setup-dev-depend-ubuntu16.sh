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

