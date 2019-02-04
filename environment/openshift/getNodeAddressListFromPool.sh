#!/bin/bash

USER_ID="$(id -u)"
SCRIPT_DIR=$(dirname $0)

# ===========================================================================
# Get the list of IP addresses from the pool
# ===========================================================================
POOL_DATA_FILE="${1}"
# -----------------------------------------------------------------------------------
#DEBUG_MESSAGES=1
# -----------------------------------------------------------------------------------
if [ -z "$POOL_DATA_FILE" ]; then
	echo "You must supply POOL_DATA_FILE."
	MissingParam=1
fi

if [ ! -z "$MissingParam" ]; then
	echo "============================================"
	echo "One or more parameters are missing!"
	echo "--------------------------------------------"	
	echo "POOL_DATA_FILE[{1}]: ${1}"
	echo "============================================"
	echo
	exit 1
fi
# ===================================================================================

read -r POOL_DATA < $POOL_DATA_FILE
ORIGINAL_IFS=$IFS
IFS=","
POOL_DATA=($POOL_DATA)

NODE_IP_LIST=""
NODE_COUNT=${#POOL_DATA[@]}

for NODE_DATA in "${POOL_DATA[@]}"; do
	IFS=" "
	NODE_DATA_ARRAY=(${NODE_DATA})
	NODE_IP=${NODE_DATA_ARRAY[1]}
	NODE_IP_LIST="${NODE_IP_LIST},${NODE_IP}"	
done
IFS=$ORIGINAL_IFS

NODE_IP_LIST="${NODE_IP_LIST:1}"
echo ${NODE_IP_LIST}