#!/bin/bash
SCRIPT_DIR=$(dirname $0)/..

NODE_DATA=$(${SCRIPT_DIR}/getNodeInfoFromPool.sh ${SCRIPT_DIR}/pool_data 0)
echo
echo "NODE_DATA: ${NODE_DATA}"

