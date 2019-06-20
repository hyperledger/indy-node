#!/bin/bash

set -e

IP="$1"
POOL_NETWORK_NAME="$2"

IMAGE_NAME="indyclient"
SCRIPT_DIR=$(dirname $0)

if [ "$IP" = "--help" ]; then
        echo "Usage: $0 <client-ip> <pool-network-name>"
        exit 1
fi

if [ -z "$POOL_NETWORK_NAME" ] || [ -z "$IP" ]; then
        echo "Invalid arguments. Try --help for usage."
        exit 1
fi

$SCRIPT_DIR/client_stop.sh

echo "Starting container $IMAGE_NAME at $IP"
# options are explained here: https://hub.docker.com/r/solita/ubuntu-systemd/
docker run -itd --rm --memory="1512m" --name=$IMAGE_NAME --ip="${IP}" --network=$POOL_NETWORK_NAME --security-opt seccomp=unconfined --tmpfs /run --tmpfs /run/lock -v /sys/fs/cgroup:/sys/fs/cgroup:ro $IMAGE_NAME

echo "Started indy client"
