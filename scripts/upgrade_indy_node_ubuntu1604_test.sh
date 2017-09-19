#!/bin/bash -x

deps="$1"
if [ -z "$deps" ] ; then
  exit 1
fi

echo "Try to donwload indy version $deps"
apt-get -y update && apt-get --download-only -y --allow-downgrades --allow-change-held-packages install $deps
ret=$?
if [ $ret -ne 0 ] ; then
  echo "Failed to obtain $deps"
  exit 1
fi

echo "Stop indy-node"
systemctl stop indy-node

echo "Run indy upgrade to $deps"
apt-get -y --allow-downgrades --allow-change-held-packages --reinstall install $deps
ret=$?
if [ $ret -ne 0 ] ; then
  echo "Upgrade to $deps failed"
fi
