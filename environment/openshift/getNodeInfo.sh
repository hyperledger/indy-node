#!/bin/bash

USER_ID="$(id -u)"
SCRIPT_DIR=$(dirname $0)

# ===========================================================================
# Get node information
# ===========================================================================
NODE_DATA="${1}"
INFO="${2}"
# -----------------------------------------------------------------------------------
#DEBUG_MESSAGES=1
# -----------------------------------------------------------------------------------
if [ -z "$NODE_DATA" ]; then
	echo "You must supply NODE_DATA."
	MissingParam=1
fi

if [ -z "$INFO" ]; then
	INFO="name"
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
# -----------------------------------------------------------------------------------
INFO="$(echo "$INFO" | tr '[:upper:]' '[:lower:]')"
if [ ${INFO} = "name" ]; then
	INDEX=0
elif [ ${INFO} = "basename" ]; then
	INDEX=0
elif [ ${INFO} = "number" ]; then
	INDEX=0
elif [ ${INFO} = "ip" ]; then
	INDEX=1
elif [ ${INFO} = "nodeport" ]; then
	INDEX=2
elif [ ${INFO} = "clientport" ]; then
	INDEX=3
else
	# Default, get node name.
	INDEX=0 
fi
# ===================================================================================

ORIGINAL_IFS=${IFS}
IFS=" "
NODE_DATA_ARRAY=(${NODE_DATA})
RTN_DATA=${NODE_DATA_ARRAY[${INDEX}]}
IFS=${ORIGINAL_IFS}

if [ ${INFO} = "name" ]; then
	RTN_DATA="$(tr '[:lower:]' '[:upper:]' <<< ${RTN_DATA:0:1})${RTN_DATA:1}"
elif [ ${INFO} = "number" ]; then
	RTN_DATA="${RTN_DATA//[!0-9]/}"
elif [ ${INFO} = "basename" ]; then
	RTN_DATA="$(tr '[:lower:]' '[:upper:]' <<< ${RTN_DATA:0:1})${RTN_DATA:1}"
	RTN_DATA="${RTN_DATA//[[:digit:]]/}"
fi

echo ${RTN_DATA}