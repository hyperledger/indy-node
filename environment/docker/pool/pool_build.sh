#!/bin/bash

set -e

POOL_DATA_FILE="$1"
BASE_IP="$2"
CNT="$3"
NODE_START_PORT="$4"
CLI_CNT="$5"
IPS="$6"
BASE_NODE_NAME="Node"
SCRIPT_DIR=$(dirname $0)
POOL_DATA=""

echo "$CNT $IPS $CLI_CNT"

if [ "$POOL_DATA_FILE" = "--help" ]; then
        echo "Usage: $0 <pool-data-file> [<base-ip>] [<node-cnt>] [<node-start-port>] [<cli-cnt>] [<pool-ips>]"
        exit 1
fi

if [ -z "$BASE_IP" ]; then
        BASE_IP="10.0.0."
fi

if [ -z "$CNT" ]; then
        CNT=4
fi

if [ -z "$CLI_CNT" ]; then
        CLI_CNT=10
fi

if [ -z "$START_PORT" ]; then
        START_PORT=9701
fi

if [ -z "$IPS" ]; then
        for i in `seq 1 $CNT`; do
                ADDR=$((i+1))
                IP="${BASE_IP}${ADDR}"
                IPS="${IPS},${IP}"
        done
        IPS=${IPS:1}
fi

if [ -z "$POOL_DATA_FILE" ]; then
        POOL_DATA_FILE="pool_data"
fi

if [ -f "$POOL_DATA_FILE" ]; then
        $SCRIPT_DIR/pool_stop.sh "$POOL_DATA_FILE" "pool-network"
fi

echo "Creating pool of ${CNT} nodes with ips ${IPS}"
PORT=$START_PORT
ORIGINAL_IFS=$IFS
IFS=','
IPS_ARRAY=($IPS)

NIP="0.0.0.0"
CIP="0.0.0.0"

IFS=$ORIGINAL_IFS
for i in `seq 1 $CNT`; do
        NODE_NAME="${BASE_NODE_NAME}${i}"
        NPORT=$PORT
        ((PORT++))
        CPORT=$PORT
        ((PORT++))
        NODE_IMAGE_TAG="$(echo "$NODE_NAME" | tr '[:upper:]' '[:lower:]')"
        POOL_DATA="${POOL_DATA},$NODE_IMAGE_TAG ${IPS_ARRAY[i-1]} $NPORT $CPORT"
        $SCRIPT_DIR/node_build.sh $NODE_NAME $NIP $NPORT $CIP $CPORT $NODE_IMAGE_TAG  "${IPS}" $CNT $CLI_CNT $i
done
POOL_DATA=${POOL_DATA:1}

echo "Writing pool data $POOL_DATA to file $POOL_DATA_FILE"
echo "$POOL_DATA" > $POOL_DATA_FILE

echo "Pool created"
