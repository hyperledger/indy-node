#!/bin/bash -x

vers="$1"
if [ -z "$vers" ] ; then
  exit 1
fi

echo "Try to donwload sovrin dependencies"
apt-get -y update && apt-get --download-only -y install python3-sovrin-common python3-plenum python3-ledger
ret=$?
if [ $ret -ne 0 ] ; then
  echo "Failed to obtain sovrin dependencies"
fi
echo "Try to donwload sovrin version $vers"
apt-get -y update && apt-get --download-only -y install sovrin-node="$vers"
ret=$?
if [ $ret -ne 0 ] ; then
  echo "Failed to obtain sovrin-node=$vers packages"
fi

echo "Stop sovrin-node"
systemctl stop sovrin-node

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
