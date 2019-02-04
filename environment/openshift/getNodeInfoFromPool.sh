#!/bin/bash

USER_ID="$(id -u)"
SCRIPT_DIR=$(dirname $0)

# ===========================================================================
# Get node information from the pool
# ===========================================================================
POOL_DATA_FILE="${1}"
NODE_INDEX="${2}"
# -----------------------------------------------------------------------------------
#DEBUG_MESSAGES=1
# -----------------------------------------------------------------------------------
if [ -z "$POOL_DATA_FILE" ]; then
	echo "You must supply POOL_DATA_FILE."
	MissingParam=1
fi

if [ -z "$NODE_INDEX" ]; then
	NODE_INDEX=0
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

read -r POOL_DATA < ${POOL_DATA_FILE}
ORIGINAL_IFS=${IFS}
IFS=","
POOL_DATA=(${POOL_DATA})
NODE_DATA=${POOL_DATA[${NODE_INDEX}]}
IFS=${ORIGINAL_IFS}

echo ${NODE_DATA}