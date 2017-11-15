#!/bin/bash -x

# Upgrade may change service files
systemctl daemon-reload
systemctl reset-failed

echo "Starting indy-node"
systemctl start indy-node

echo "Restarting agent"
systemctl restart indy-node-control
