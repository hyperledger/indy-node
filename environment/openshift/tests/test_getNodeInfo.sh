#!/bin/bash
SCRIPT_DIR=$(dirname $0)/..

NODE_DATA=$(${SCRIPT_DIR}/getNodeInfoFromPool.sh ${SCRIPT_DIR}/pool_data)

NODE_NAME=$(${SCRIPT_DIR}/getNodeInfo.sh "${NODE_DATA}" "name")
BASE_NODE_NAME=$(${SCRIPT_DIR}/getNodeInfo.sh "${NODE_DATA}" "basename")
NODE_NUMBER=$(${SCRIPT_DIR}/getNodeInfo.sh "${NODE_DATA}" "number")
NODE_IP=$(${SCRIPT_DIR}/getNodeInfo.sh "${NODE_DATA}" "ip")
NODE_PORT=$(${SCRIPT_DIR}/getNodeInfo.sh "${NODE_DATA}" "nodeport")
CLIENT_PORT=$(${SCRIPT_DIR}/getNodeInfo.sh "${NODE_DATA}" "clientport")

echo
echo "NODE_DATA: ${NODE_DATA}"
echo "NODE_NAME: ${NODE_NAME}"
echo "BASE_NODE_NAME: ${BASE_NODE_NAME}"
echo "NODE_NUMBER: ${NODE_NUMBER}"
echo "NODE_IP: ${NODE_IP}"
echo "NODE_PORT: ${NODE_PORT}"
echo "CLIENT_PORT: ${CLIENT_PORT}"

