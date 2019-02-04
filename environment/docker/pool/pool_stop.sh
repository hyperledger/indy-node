#!/bin/bash

set -e

POOL_DATA_FILE="$1"
POOL_NETWORK_NAME="$2"

SCRIPT_DIR=$(dirname $0)
POOL_DATA=""

if [ "$POOL_DATA_FILE" = "--help" ]; then
        echo "Usage: $0 [<pool-data-file>] [<pool-network-name>]"
        exit 1
fi

if [ -z "$POOL_DATA_FILE" ]; then
        POOL_DATA_FILE="pool_data"
fi

if [ ! -f "$POOL_DATA_FILE" ]; then
        echo "File $POOL_DATA_FILE not present: exiting"
        exit 0
fi

if [ -z "$POOL_NETWORK_NAME" ]; then
        POOL_NETWORK_NAME="pool-network"
fi

echo "Reading pool data"
read -r POOL_DATA < "$POOL_DATA_FILE"
echo "Pool data is ${POOL_DATA}"
ORIGINAL_IFS=$IFS
IFS=","
POOL_DATA=($POOL_DATA)

echo "Stopping pool and removing containers"
for NODE_DATA in "${POOL_DATA[@]}"; do
        IFS=" "
        NODE_DATA=($NODE_DATA)
        IMAGE_NAME=${NODE_DATA[0]}
        NODE_IP=${NODE_DATA[1]}
        NODE_PORT=${NODE_DATA[2]}
        CLI_PORT=${NODE_DATA[3]}
        (($(docker ps -f name="$IMAGE_NAME" | grep -w "$IMAGE_NAME" | wc -l))) || continue
        docker stop -t 15 $IMAGE_NAME
        docker rm $IMAGE_NAME
        echo "Removed container $IMAGE_NAME"
done
IFS=$ORIGINAL_IFS
echo "Pool stopped and all containers removed"

if [[ $(docker network ls -f name="$POOL_NETWORK_NAME" | grep -w "$POOL_NETWORK_NAME" | wc -l) -gt 0 ]]; then
        echo "Removing pool network"
        docker network rm $POOL_NETWORK_NAME
        echo "$POOL_NETWORK_NAME removed"
fi

[ -f "$POOL_DATA_FILE" ] && rm "$POOL_DATA_FILE"
