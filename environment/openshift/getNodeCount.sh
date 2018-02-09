#!/bin/bash

USER_ID="$(id -u)"
SCRIPT_DIR=$(dirname $0)

# ===========================================================================
# Get the node count from a csv list of node information.
# ===========================================================================
NODE_DATA="${1}"
# -----------------------------------------------------------------------------------
#DEBUG_MESSAGES=1
# -----------------------------------------------------------------------------------
if [ -z "$NODE_DATA" ]; then
	echo "You must supply NODE_DATA."
	MissingParam=1
fi

if [ ! -z "$MissingParam" ]; then
	echo "============================================"
	echo "One or more parameters are missing!"
	echo "--------------------------------------------"	
	echo "NODE_DATA[{1}]: ${1}"
	echo "============================================"
	echo
	exit 1
fi
# ===================================================================================

ORIGINAL_IFS=$IFS
IFS=","
NODE_DATA=($NODE_DATA)
NODE_COUNT=${#NODE_DATA[@]}
IFS=$ORIGINAL_IFS

echo ${NODE_COUNT}