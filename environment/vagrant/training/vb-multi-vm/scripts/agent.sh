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
apt-get install -y software-properties-common python-software-properties
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88
add-apt-repository "deb https://repo.sovrin.org/deb xenial master"
apt-get update
#DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
DEBIAN_FRONTEND=noninteractive apt-get install -y unzip make screen indy-node tmux vim wget

awk '{if (index($1, "NETWORK_NAME") != 0) {print("NETWORK_NAME = \"sandbox\"")} else print($0)}' /etc/indy/indy_config.py> /tmp/indy_config.py
mv /tmp/indy_config.py /etc/indy/indy_config.py

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
