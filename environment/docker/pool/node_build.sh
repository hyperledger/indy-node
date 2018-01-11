#!/bin/bash

NODE_NAME="$1"
NPORT="$2"
CPORT="$3"
NODE_IMAGE_TAG="$4"
IPS="$5"
CNT="$6"
CLI_CNT="$7"
NODE_NUM="$8"
NODE_IMAGE_TAG="$9"

SCRIPT_DIR=$(dirname $0)
USER_ID="$(id -u)"

if [ "$NODE_NAME" = "--help" ] ; then
        echo "Usage: $0 <node-name> <node-port> <client-port> <node-image-tag> <cluster-ips> <node-cnt> <cli-cnt> <node-num>"
        exit 1
fi

if [ -z "$NODE_NAME" ] || [ -z "$NPORT" ] || [ -z "$CPORT" ]; then
        echo "Incorrect input. Type $0 --help for help."
	exit 1
fi

if [ -z "$NODE_IMAGE_TAG" ]; then
	NODE_IMAGE_TAG="$(echo "$NODE_NAME" | tr '[:upper:]' '[:lower:]')"
fi

echo "Creating a new node ${NODE_NAME} ${NPORT} ${CPORT}"

echo "Setting up docker with systemd"
docker run --rm --privileged -v /:/host solita/ubuntu-systemd setup

echo "Building indybase"
docker build -t 'indybase' -f ${SCRIPT_DIR}/base.systemd.ubuntu.dockerfile $SCRIPT_DIR
echo "Building indycore for user ${USER_ID}"
docker build -t 'indycore' --build-arg uid=$USER_ID -f ${SCRIPT_DIR}/core.ubuntu.dockerfile $SCRIPT_DIR
echo "Building $NODE_IMAGE_TAG"
docker build -t "$NODE_IMAGE_TAG" --build-arg nodename=$NODE_NAME --build-arg nport=$NPORT --build-arg cport=$CPORT --build-arg ips=$IPS --build-arg nodenum=$NODE_NUM --build-arg nodecnt=$CNT --build-arg clicnt=$CLI_CNT -f ${SCRIPT_DIR}/node.init.ubuntu.dockerfile $SCRIPT_DIR

echo "Node ${NODE_NAME} ${NPORT} ${CPORT} created"
