#!/bin/bash

CNT="$1"
IPS="$2"
CLI_CNT="$3"
START_PORT="$4"
POOL_NETWORK_NAME="${5:-pool-network}"
SCRIPT_DIR=$(dirname $0)
POOL_DATA_FILE="pool_data"
BASE_IP="10.0.0."
POOL_DATA=""

if [ "$CNT" = "--help" ]; then
        echo "Usage: $0 <node-cnt> <pool-ips> <cli-cnt> <node-start-port> [<pool-network-name>]"
        exit 1
fi

echo "Creating pool"
$SCRIPT_DIR/pool_build.sh "$POOL_DATA_FILE" $BASE_IP $CNT $START_PORT $CLI_CNT $IPS

echo "Reading pool data"
read -r POOL_DATA < "$POOL_DATA_FILE"
echo "Pool data is ${POOL_DATA}"
ORIGINAL_IFS=$IFS
IFS=","
POOL_DATA=($POOL_DATA)

echo "Creating pool network $POOL_NETWORK_NAME"
SUBNET="${BASE_IP}0/8"
(($(docker network ls -f name="$POOL_NETWORK_NAME" | grep -w "$POOL_NETWORK_NAME" | wc -l))) && docker network rm "$POOL_NETWORK_NAME"
docker network create --subnet=$SUBNET "$POOL_NETWORK_NAME"

echo "Starting pool"
for NODE_DATA in "${POOL_DATA[@]}"; do
        IFS=" "
        NODE_DATA=($NODE_DATA)
        IMAGE_NAME=${NODE_DATA[0]}
        NODE_IP=${NODE_DATA[1]}
        NODE_PORT=${NODE_DATA[2]}
        CLI_PORT=${NODE_DATA[3]}
        $SCRIPT_DIR/node_start.sh "$IMAGE_NAME" $NODE_IP "$POOL_NETWORK_NAME" $NODE_PORT $CLI_PORT
done
IFS=$ORIGINAL_IFS
echo "Pool started"
