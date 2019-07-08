#!/bin/bash
set -e

echo 'Setting up https for apt...'
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates
echo 'Set up https for apt'

echo 'Adding repositories and keys...'
sudo add-apt-repository "deb http://us.archive.ubuntu.com/ubuntu xenial main universe"
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88

sudo add-apt-repository "deb https://repo.sovrin.org/deb xenial master"
sudo add-apt-repository "deb https://repo.sovrin.org/sdk/deb xenial stable"
sudo apt-get update
echo 'Added repositories and keys'


echo 'Installing libsodium...'
sudo apt-get install -y libsodium18
echo 'Installed libsodium'


echo 'Installing RocksDB...'
sudo apt-get install -y libbz2-dev \
    zlib1g-dev \
    liblz4-dev \
    libsnappy-dev \
    rocksdb=5.8.8
echo 'Installed RocksDB'


echo 'Installing Libindy and Libindy Crypto...'
sudo apt-get install -y libindy libindy-crypto
echo 'Installed Libindy and Libindy Crypto'
