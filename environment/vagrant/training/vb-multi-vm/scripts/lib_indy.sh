#!/bin/bash

display_usage() {
	echo "Usage:\t$0 <TIMEZONE> "
	echo "EXAMPLE: $0 /usr/share/zoneinfo/America/Denver"
}

# if less than one argument is supplied, display usage
if [  $# -ne 1 ]
then
    display_usage
    exit 1
fi

TIMEZONE=$1


#--------------------------------------------------------
echo 'Setting Up Networking'
cp /vagrant/etc/hosts /etc/hosts
perl -p -i -e 's/(PasswordAuthentication\s+)no/$1yes/' /etc/ssh/sshd_config
service sshd restart

#--------------------------------------------------------
echo 'Setting up timezone'
cp $TIMEZONE /etc/localtime

#--------------------------------------------------------
echo "Installing Required Packages"
apt-get update
apt-get install -y software-properties-common python-software-properties libsodium18
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88
add-apt-repository "deb https://repo.sovrin.org/deb xenial stable"
add-apt-repository "deb https://repo.sovrin.org/sdk/deb xenial stable"
add-apt-repository ppa:jonathonf/python-3.6
apt-get update
apt-get install python3.6 -y
DEBIAN_FRONTEND=noninteractive apt-get install -y tmux vim wget dialog figlet unzip make screen python3-pip libindy

#-------------------------------------------------------
echo "Setting up the python wrapper"
pip3 install python3-indy
pip3 install --upgrade python3-indy
ln -s /usr/local/lib/python3.5/dist-packages/indy /usr/local/lib/python3.6/dist-packages/indy

#--------------------------------------------------------
echo 'Cleaning Up'
rm /etc/update-motd.d/10-help-text
rm /etc/update-motd.d/97-overlayroot
apt-get update
#DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
updatedb
