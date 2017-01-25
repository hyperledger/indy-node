#!/bin/bash -x

vers="$1"
if [ -z "$vers" ] ; then
  exit 1
fi

systemctl stop sovrin-node

echo "Run sovrin upgrade to version $vers"
apt-get update -y && apt-get install sovrin-node="$vers"
ret=$?
if [ $ret -ne 0 ] ; then
  echo "Upgrade to version $vers failed"
  exit 1
fi

systemctl start sovrin-node

echo "Restarting an agent"
systemctl restart sovrin_node_control
