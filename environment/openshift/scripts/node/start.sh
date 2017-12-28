#!/bin/bash
SCRIPT_DIR=$(dirname $0)

$SCRIPT_DIR/initialize.sh

echo "Starting sovrin node ..."
echo

# echo "Starting indy-node-control service ..."
# echo "/usr/bin/env python3 -O /usr/local/bin/start_node_control_tool.py ${TEST_MODE} --hold-ext ${HOLD_EXT}"
# echo
# exec /usr/bin/env python3 -O /usr/local/bin/start_node_control_tool.py ${TEST_MODE} --hold-ext ${HOLD_EXT} &
# sleep 10

echo "Starting sovrin-node service ..."
echo "/usr/bin/env python3 -O /usr/local/bin/start_indy_node ${NODE_NAME} ${NODE_PORT} ${CLIENT_PORT}"
echo
exec /usr/bin/env python3 -O /usr/local/bin/start_indy_node ${NODE_NAME} ${NODE_PORT} ${CLIENT_PORT}

# echo "Sovrin node started."