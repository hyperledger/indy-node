#!/bin/bash -x

vers="$1"
if [ -z "$vers" ] ; then
  exit 1
fi


echo "Try to donwload sovrin dependencies"
apt-get -y update && apt-get --download-only -y install sovrin-common plenum ledger
ret=$?
if [ $ret -ne 0 ] ; then
  echo "Failed to obtain sovrin dependencies"
  exit 1
fi
echo "Try to donwload sovrin version $vers"
apt-get -y update && apt-get --download-only -y install sovrin-node="$vers"
ret=$?
if [ $ret -ne 0 ] ; then
  echo "Failed to obtain sovrin-node=$vers packages"
  exit 1
fi

echo "Stop sovrin-node"
systemctl stop sovrin-node

echo "Run sovrin dependencies upgrade to latest version"
apt-get -y install plenum sovrin-common ledger
ret=$?
if [ $ret -ne 0 ] ; then
  echo "Upgrade of dependencies to lastest version failed"
  exit 1
fi
echo "Run sovrin upgrade to version $vers"
apt-get -y install sovrin-node="$vers"
ret=$?
if [ $ret -ne 0 ] ; then
  echo "Upgrade to version $vers failed"
  exit 1
fi

# Upgrade may change service files
systemctl daemon-reload

echo "Starting sovrin-node"
systemctl start sovrin-node

echo "Restarting agent"
systemctl restart sovrin-node-control
