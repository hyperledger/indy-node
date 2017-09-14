#!/bin/bash -x
# Upgrade may change service files
systemctl daemon-reload

echo "Starting sovrin-node"
systemctl start sovrin-node

echo "Restarting agent"
systemctl restart sovrin-node-control
