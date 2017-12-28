#!/bin/bash
SCRIPT_DIR=$(dirname $0)

$SCRIPT_DIR/initialize.sh



echo "Starting sovrin client node ..."
echo "The sovrin cli will not keep the pod running, so instead we'll sleep for infinity."
echo "To use the sovrin cli, rsh into the pod and run the cli in the session."
echo
sleep infinity
# sovrin