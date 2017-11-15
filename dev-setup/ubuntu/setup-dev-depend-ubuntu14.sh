#!/bin/bash

echo 'Adding repositories and keys...'

sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys B9316A7BC7917B12
echo "deb http://ppa.launchpad.net/chris-lea/libsodium/ubuntu trusty main" | sudo tee -a /etc/apt/sources.list
echo "deb-src http://ppa.launchpad.net/chris-lea/libsodium/ubuntu trusty main" | sudo tee -a /etc/apt/sources.list

sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 68DB5E88
echo "deb https://repo.sovrin.org/deb xenial stable" | sudo tee -a /etc/apt/sources.list

sudo apt-get update

echo 'Added repositories and keys'

echo 'Installing libsodium...'
sudo apt-get install libsodium13
echo 'Installed libsodium'


echo 'Installing Charm Crypto...'
sudo apt-get install python3-charm-crypto
echo 'Installed Charm Crypto'


echo 'Installing Libindy Crypto...'
sudo apt-get install libindy-crypto
echo 'Installed Libindy Crypto'