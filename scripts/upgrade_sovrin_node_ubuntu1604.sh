#!/bin/bash -x

vers="$1"
if [ -z "$vers" ] ; then
  exit 1
fi

echo "Run sovrin upgrade to version $vers"
apt-get update -y && apt-get install sovrin-node="$vers"
ret=$?
if [ $ret -ne 0 ] ; then
  echo "Upgrade to version $vers failed"
  exit 1
fi

echo "Restarting node and agent"
systemctl restart sovrin-node
systemctl restart sovrin_node_control
