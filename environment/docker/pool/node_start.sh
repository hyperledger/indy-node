#!/bin/bash

set -e

IMAGE_NAME="$1"
NODE_IP="$2"
POOL_NETWORK_NAME="$3"
NODE_PORT="$4"
CLI_PORT="$5"

SCRIPT_DIR=$(dirname $0)

if [ "$IMAGE_NAME" = "--help" ]; then
        echo "Usage: $0 <image-name> <node-ip> <pool-network-name>"
        exit 1
fi

if [ -z "$POOL_NETWORK_NAME" ] || [ -z "$IMAGE_NAME" ] || [ -z "$NODE_IP" ]; then
        echo "Invalid arguments. Try --help for usage."
        exit 1
fi

if [[ $(docker ps -f name="$IMAGE_NAME" | grep -w "$IMAGE_NAME" | wc -l) -gt 0 ]]; then
        echo "Removing old container $IMAGE_NAME"
        docker rm -fv "$IMAGE_NAME"
fi

echo "Starting node $IMAGE_NAME $NODE_IP"
docker run -tid --privileged -p $NODE_PORT:$NODE_PORT -p $CLI_PORT:$CLI_PORT --memory="1512m" --name=$IMAGE_NAME --ip="${NODE_IP}" --network=$POOL_NETWORK_NAME --security-opt seccomp=unconfined --tmpfs /run --tmpfs /run/lock -v /sys/fs/cgroup:/sys/fs/cgroup:ro $IMAGE_NAME
docker exec -td $IMAGE_NAME systemctl start indy-node
echo "Node $IMAGE_NAME started on $NODE_IP"
