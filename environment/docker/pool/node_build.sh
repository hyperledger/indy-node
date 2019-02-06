#!/bin/bash

set -e

NODE_NAME="$1"
NIP="$2"
NPORT="$3"
CIP="$4"
CPORT="$5"
NODE_IMAGE_TAG="$6"
IPS="$7"
CNT="$8"
CLI_CNT="$9"
NODE_NUM="${10}"
NODE_IMAGE_TAG="${11}"

SCRIPT_DIR=$(dirname $0)
USER_ID="$(id -u)"

if [ "$NODE_NAME" = "--help" ] ; then
        echo "Usage: $0 <node-name> <node-ip> <node-port> <client-ip> <client-port> <node-image-tag> <cluster-ips> <node-cnt> <cli-cnt> <node-num>"
        exit 1
fi

if [ -z "$NODE_NAME" ] || [ -z "$NIP" ] || [ -z "$NPORT" ] || [ -z "$CIP" ] || [ -z "$CPORT" ]; then
        echo "Incorrect input. Type $0 --help for help."
	exit 1
fi

if [ -z "$NODE_IMAGE_TAG" ]; then
	NODE_IMAGE_TAG="$(echo "$NODE_NAME" | tr '[:upper:]' '[:lower:]')"
fi

echo "Creating a new node ${NODE_NAME} ${NIP} ${NPORT} ${CIP} ${CPORT}"

echo "Setting up docker with systemd"
docker run --rm --privileged -v /:/host solita/ubuntu-systemd setup

echo "Building indybase"
docker build -t 'indybase' -f ${SCRIPT_DIR}/base.systemd.ubuntu.dockerfile $SCRIPT_DIR
echo "Building indycore for user ${USER_ID}"
docker build -t 'indycore' --build-arg uid=$USER_ID -f ${SCRIPT_DIR}/core.ubuntu.dockerfile $SCRIPT_DIR
echo "Building $NODE_IMAGE_TAG"
docker build -t "$NODE_IMAGE_TAG"   \
    --build-arg nodename=$NODE_NAME \
    --build-arg nip=$NIP            \
    --build-arg nport=$NPORT        \
    --build-arg cip=$CIP            \
    --build-arg cport=$CPORT        \
    --build-arg ips=$IPS            \
    --build-arg nodenum=$NODE_NUM   \
    --build-arg nodecnt=$CNT        \
    --build-arg clicnt=$CLI_CNT     \
    -f ${SCRIPT_DIR}/node.init.ubuntu.dockerfile $SCRIPT_DIR

echo "Node ${NODE_NAME} ${NIP} ${NPORT} ${CIP} ${CPORT} created"
