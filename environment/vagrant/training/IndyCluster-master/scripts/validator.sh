#!/bin/bash

HOSTNAME=$1
NODEIP=$2
NODEPORT=$2
CLIENTIP=$3
CLIENTPORT=$3

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
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88
add-apt-repository "deb https://repo.evernym.com/deb xenial master"
add-apt-repository "deb https://repo.sovrin.org/deb xenial master"
apt-get update
#DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
DEBIAN_FRONTEND=noninteractive apt-get install -y dialog figlet python-pip python3-pip python3.5-dev unzip make screen indy-node tmux vim wget

#--------------------------------------------------------
echo 'Setting Up Indy Node'
su - indy -c "init_indy_node $HOSTNAME $NODEIP $NODEPORT $CLIENTIP $CLIENTPORT"
systemctl start indy-node
systemctl enable indy-node
systemctl status indy-node.service
su - indy -c "generate_indy_pool_transactions --nodes 4 --clients 4 --ips '10.20.30.201,10.20.30.202,10.20.30.203,10.20.30.204'"

#--------------------------------------------------------
echo 'Fixing Bugs'
if grep -Fxq '[Install]' /etc/systemd/system/indy-node.service
then
  echo '[Install] section is present in indy-node target'
else 
  perl -p -i -e 's/\\n\\n/[Install]\\nWantedBy=multi-user.target\\n/' /etc/systemd/system/indy-node.service
fi
chmod -x /etc/systemd/system/orientdb.service
if grep -Fxq 'SendMonitorStats' /etc/indy/indy_config.py
then
  echo 'SendMonitorStats is configured in indy_config.py'
else
  printf "\n%s\n" "SendMonitorStats = False" >> /etc/indy/indy_config.py
fi
chown indy:indy /etc/indy/indy_config.py

#--------------------------------------------------------
echo 'Cleaning Up'
rm /etc/update-motd.d/10-help-text
rm /etc/update-motd.d/97-overlayroot
apt-get update
#DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
updatedb
