#!/bin/bash
SCRIPT_DIR=$(dirname $0)

$SCRIPT_DIR/initialize.sh



echo "Starting indy client node ..."
echo "The indy cli will not keep the pod running, so instead we'll sleep for infinity."
echo "To use the indy cli, rsh into the pod and run the cli in the session."
echo
sleep infinity
# indy