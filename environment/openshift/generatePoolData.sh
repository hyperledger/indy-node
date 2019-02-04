#!/bin/bash

USER_ID="$(id -u)"
SCRIPT_DIR=$(dirname $0)

# ===========================================================================
# Generate node pool data
# ===========================================================================
POOL_DATA_FILE=${1}
BASE_NODE_NAME=${2}
BASE_IP=${3}
NODE_COUNT=${4}
CLIENT_COUNT=${5}
START_PORT=${6}
NODE_IP_LIST=${7}
# -----------------------------------------------------------------------------------
#DEBUG_MESSAGES=1
# -----------------------------------------------------------------------------------
if [ -z "$POOL_DATA_FILE" ]; then
	POOL_DATA_FILE="pool_data"
fi

if [ -z "$BASE_NODE_NAME" ]; then
	BASE_NODE_NAME="Node"
fi

if [ -z "$BASE_IP" ]; then
  BASE_IP="10.0.0."
fi

if [ -z "$NODE_COUNT" ]; then
  NODE_COUNT=4
fi

if [ -z "$CLIENT_COUNT" ]; then
  CLIENT_COUNT=10
fi

if [ -z "$START_PORT" ]; then
  START_PORT=9701
fi

if [ -z "$NODE_IP_LIST" ]; then
  for i in `seq 1 $NODE_COUNT`; do
    NODE_ADDRESS=$((i+1))
	NODE_IP="${BASE_IP}${NODE_ADDRESS}"
	NODE_IP_LIST="${NODE_IP_LIST},${NODE_IP}"
  done
  NODE_IP_LIST=${NODE_IP_LIST:1}
fi
# ===================================================================================

echo "Creating pool of ${NODE_COUNT} nodes with ips ${NODE_IP_LIST} ..."

PORT=${START_PORT}
ORIGINAL_IFS=${IFS}
IFS=','
IPS_ARRAY=(${NODE_IP_LIST})
IFS=${ORIGINAL_IFS}

for i in `seq 1 $NODE_COUNT`; do
	NODE_NAME="${BASE_NODE_NAME}${i}"
	NODE_PORT=${PORT}
	((PORT++))
	CLIENT_PORT=${PORT}
	((PORT++))
	NODE_NAME="$(echo "${NODE_NAME}" | tr '[:upper:]' '[:lower:]')"
	POOL_DATA="${POOL_DATA},${NODE_NAME} ${IPS_ARRAY[i-1]} ${NODE_PORT} ${CLIENT_PORT}"	
done

POOL_DATA=${POOL_DATA:1}
echo "Writing node pool data to ${POOL_DATA_FILE} for referance ..."
echo "${POOL_DATA}" > ${POOL_DATA_FILE}
echo "Node pool data created."
echo
