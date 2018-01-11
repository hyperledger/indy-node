#!/bin/bash

display_usage() {
	echo -e "Usage:\t$0 <NODENAME> <NODEPORT> <CLIENTPORT> <TIMEZONE>"
	echo -e "EXAMPLE: $0 Node1 9701 9702 /usr/share/zoneinfo/America/Denver"
}

# if less than one argument is supplied, display usage
if [  $# -ne 4 ]
then
    display_usage
    exit 1
fi

HOSTNAME=$1
NODEPORT=$2
CLIENTPORT=$3
TIMEZONE=$4


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
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 68DB5E88
add-apt-repository "deb https://repo.sovrin.org/deb xenial master"
apt-get update
#DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
DEBIAN_FRONTEND=noninteractive apt-get install -y unzip make screen sovrin tmux vim wget

#--------------------------------------------------------
[[ $HOSTNAME =~ [^0-9]*([0-9]*) ]]
NODENUM=${BASH_REMATCH[1]}
echo "Setting Up Indy Node Number $NODENUM"
su - indy -c "init_indy_node $HOSTNAME $NODEPORT $CLIENTPORT"  # set up /etc/indy/indy.env
su - indy -c "generate_indy_pool_transactions --nodes 4 --clients 4 --nodeNum $NODENUM --ips '10.20.30.201,10.20.30.202,10.20.30.203,10.20.30.204'"
systemctl start indy-node
systemctl enable indy-node
systemctl status indy-node.service

#--------------------------------------------------------
echo 'Fixing Bugs'
if grep -Fxq '[Install]' /etc/systemd/system/indy-node.service
then
  echo '[Install] section is present in indy-node target'
else
  perl -p -i -e 's/\\n\\n/[Install]\\nWantedBy=multi-user.target\\n/' /etc/systemd/system/indy-node.service
fi
if grep -Fxq 'SendMonitorStats' /etc/indy/indy_config.py
then
  echo 'SendMonitorStats is configured in indy_config.py'
else
  echo 'SendMonitorStats = False' >> /etc/indy/indy_config.py
fi
chown indy:indy /etc/indy/indy_config.py
echo "Setting Up Indy Node Number $NODENUM"
su - indy -c "init_indy_node $HOSTNAME $NODEPORT $CLIENTPORT"  # set up /etc/indy/indy.env
su - indy -c "generate_indy_pool_transactions --nodes 4 --clients 4 --nodeNum $NODENUM --ips '10.20.30.201,10.20.30.202,10.20.30.203,10.20.30.204'"
systemctl start indy-node
systemctl enable indy-node
systemctl status indy-node.service

#--------------------------------------------------------
echo 'Cleaning Up'
rm /etc/update-motd.d/10-help-text
rm /etc/update-motd.d/97-overlayroot
apt-get update
#DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
updatedb
