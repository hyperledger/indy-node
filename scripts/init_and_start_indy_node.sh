#!/bin/bash
  
: "${ALIAS?The ALIAS environment variable is not set}"
: "${SEED?The SEED environment variable is not set}"
: "${NODE_PORT:=9701}"
: "${CLIENT_PORT:=9702}"

set -e

echo "Initializing indy node ..."
init_indy_node $ALIAS $NODE_PORT $CLIENT_PORT $SEED

echo "Starting indy node ..."
python3 -O /usr/local/bin/start_indy_node $ALIAS $NODE_PORT $CLIENT_PORT
