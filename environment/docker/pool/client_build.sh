#!/bin/bash

IPS="$1"
CNT="$2"
CLI_CNT="$3"

SCRIPT_DIR=$(dirname $0)
USER_ID="$(id -u)"

if [ "$IPS" = "--help" ] ; then
        echo "Usage: $0 [<pool-ips>] [<node-cnt>] [<cli-cnt>]"
        exit 1
fi

echo "Creating a new client"

echo "Setting up docker with systemd"
docker run --rm --privileged -v /:/host solita/ubuntu-systemd setup

echo "Building sovrinbase"
docker build -t 'sovrinbase' -f ${SCRIPT_DIR}/base.systemd.ubuntu.dockerfile $SCRIPT_DIR
echo "Building sovrincore for user ${USER_ID}"
docker build -t 'sovrincore' --build-arg uid=$USER_ID -f ${SCRIPT_DIR}/core.ubuntu.dockerfile $SCRIPT_DIR
echo "Building sovrinclient"
docker build -t 'sovrinclient' --build-arg ips=$IPS --build-arg nodecnt=$CNT --build-arg clicnt=$CLI_CNT -f ${SCRIPT_DIR}/client.ubuntu.dockerfile $SCRIPT_DIR

echo "Indy client created"
