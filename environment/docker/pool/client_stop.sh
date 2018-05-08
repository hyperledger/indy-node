#!/bin/bash

IMAGE_NAME="indyclient"
SCRIPT_DIR=$(dirname $0)

if [ "$1" = "--help" ]; then
	echo "Usage: $0"
	exit 1
fi

if [ "$(docker ps --filter name=$IMAGE_NAME | grep -w $IMAGE_NAME | wc -l)" -gt "0" ]; then
	echo "Stopping and removing old $IMAGE_NAME container"
	docker stop $IMAGE_NAME
fi
