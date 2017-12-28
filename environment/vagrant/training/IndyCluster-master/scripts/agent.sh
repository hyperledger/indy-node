#!/bin/bash

#--------------------------------------------------------
echo 'Setting Up Networking'
cp /vagrant/etc/hosts /etc/hosts
perl -p -i -e 's/(PasswordAuthentication\s+)no/$1yes/' /etc/ssh/sshd_config
service sshd restart

#--------------------------------------------------------
echo "Installing Required Packages"
apt-get update
apt-get install -y software-properties-common python-software-properties
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys BD33704C
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 68DB5E88
add-apt-repository "deb https://repo.evernym.com/deb xenial master"
add-apt-repository "deb https://repo.sovrin.org/deb xenial master"
apt-get update
#DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
DEBIAN_FRONTEND=noninteractive apt-get install -y dialog figlet python-pip python3-pip python3.5-dev libsodium18 unzip make screen sovrin tmux vim wget

#--------------------------------------------------------
echo 'Generating Genesis Transaction Files'
su - vagrant -c "generate_indy_pool_transactions --nodes 4 --clients 4 --ips '10.20.30.201,10.20.30.202,10.20.30.203,10.20.30.204'"

#--------------------------------------------------------
echo 'Cleaning Up'
rm /etc/update-motd.d/10-help-text
rm /etc/update-motd.d/97-overlayroot
apt-get update
#DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
updatedb
