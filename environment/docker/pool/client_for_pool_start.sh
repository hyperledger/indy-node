#!/bin/bash

POOL_DATA_FILE="$1"
IP="$2"
CLI_CNT="$3"

SCRIPT_DIR=$(dirname $0)
POOL_NETWORK_NAME="pool-network"
POOL_DATA=""

if [ "$POOL_DATA_FILE" = "--help" ]; then
        echo "Usage: $0 <pool-data-file> <client-ip> <cli-cnt>"
        exit 1
fi

if [ -z "$CLI_CNT" ]; then
	CLI_CNT=10
fi

if [ -z "$POOL_DATA_FILE" ]; then
	POOL_DATA_FILE="pool_data"
fi

echo "Reading pool data"
read -r POOL_DATA < $POOL_DATA_FILE
echo "Pool data is ${POOL_DATA}"
ORIGINAL_IFS=$IFS
IFS=","
POOL_DATA=($POOL_DATA)

echo "Processing pool data"
IPS=""
CNT=${#POOL_DATA[@]}
LAST_NODE_IP=""
for NODE_DATA in "${POOL_DATA[@]}"; do
	IFS=" "
	NODE_DATA=($NODE_DATA)
	IMAGE_NAME=${NODE_DATA[0]}
	NODE_IP=${NODE_DATA[1]}
	NODE_PORT=${NODE_DATA[2]}
	CLI_PORT=${NODE_DATA[3]}
	LAST_NODE_IP=$NODE_IP
	IPS="${IPS},${NODE_IP}"
done
IPS=${IPS:1}
IFS=$ORIGINAL_IFS
echo "IPs are ${IPS}"
echo "Node cnt is ${CNT}"

if [ -z "$IP" ]; then
	IP_REGEXP="([0-9]+\\.[0-9]+\\.[0-9]+\\.)([0-9]+)"
	BASE_IP=$(echo "$LAST_NODE_IP" | sed -r "s/${IP_REGEXP}/\1/")
	LAST_GROUP=$(echo "$LAST_NODE_IP" | sed -r "s/${IP_REGEXP}/\2/")
	((LAST_GROUP++))
	IP="${BASE_IP}${LAST_GROUP}"
fi
echo "Client IP is ${IP}"

echo "Building client"
$SCRIPT_DIR/client_build.sh "$IPS" $CNT $CLI_CNT

echo "Starting client"
$SCRIPT_DIR/client_start.sh $IP $POOL_NETWORK_NAME

echo "Client is closed."
