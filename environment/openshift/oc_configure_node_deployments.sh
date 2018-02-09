#!/bin/bash

USER_ID="$(id -u)"
SCRIPT_DIR=$(dirname $0)

# ===========================================================================
# Generate a Node Deployment Configurations
# ===========================================================================
POOL_DATA_FILE="${1}"
CLIENT_COUNT="${2}"
DEPLOYMENT_CONFIG_TEMPLATE="${3}"
DEPLOYMENT_CONFIG_POST_FIX="${4}"
SOURCE_IMAGE_NAME="${5}"
IMAGE_TAG="${6}"
NODE_IP_LIST="${7}"
HOME_DIRECTORY="${8}"
NODE_SERVICE_HOST_PATTERN="${9}"
# -----------------------------------------------------------------------------------
#DEBUG_MESSAGES=1
# -----------------------------------------------------------------------------------
if [ -z "$POOL_DATA_FILE" ]; then
	echo "You must supply POOL_DATA_FILE."
	MissingParam=1
fi

if [ -z "$CLIENT_COUNT" ]; then
	echo "You must supply CLIENT_COUNT."
	MissingParam=1
fi

if [ -z "$DEPLOYMENT_CONFIG_TEMPLATE" ]; then
	echo "You must supply DEPLOYMENT_CONFIG_TEMPLATE."
	MissingParam=1
fi

if [ -z "$DEPLOYMENT_CONFIG_POST_FIX" ]; then
	echo "You must supply DEPLOYMENT_CONFIG_POST_FIX."
	MissingParam=1
fi

if [ -z "$SOURCE_IMAGE_NAME" ]; then
	echo "You must supply SOURCE_IMAGE_NAME."
	MissingParam=1
fi

if [ -z "$IMAGE_TAG" ]; then
	echo "You must supply IMAGE_TAG."
	MissingParam=1
fi

if [ -z "$NODE_IP_LIST" ]; then
	echo "You must supply NODE_IP_LIST."
	MissingParam=1
fi

if [ -z "$HOME_DIRECTORY" ]; then
	echo "You must supply HOME_DIRECTORY."
	MissingParam=1
fi

if [ -z "$NODE_SERVICE_HOST_PATTERN" ]; then
	echo "You must supply NODE_SERVICE_HOST_PATTERN."
	MissingParam=1
fi

if [ ! -z "$MissingParam" ]; then
	echo "============================================"
	echo "One or more parameters are missing!"
	echo "--------------------------------------------"	
	echo "POOL_DATA_FILE[{1}]: ${1}"
	echo "CLIENT_COUNT[{2}]: ${2}"
	echo "DEPLOYMENT_CONFIG_TEMPLATE[{3}]: ${3}"
	echo "DEPLOYMENT_CONFIG_POST_FIX[{4}]: ${4}"
	echo "SOURCE_IMAGE_NAME[{5}]: ${5}"
	echo "IMAGE_TAG[{6}]: ${6}"
	echo "NODE_IP_LIST[{7}]: ${7}"
	echo "HOME_DIRECTORY[{8}]: ${8}"
	echo "NODE_SERVICE_HOST_PATTERN[{9}]: ${9}"
	echo "============================================"
	echo
	exit 1
fi
# ===================================================================================

read -r POOL_DATA < $POOL_DATA_FILE
ORIGINAL_IFS=$IFS
IFS=","
POOL_DATA=($POOL_DATA)
NODE_COUNT=${#POOL_DATA[@]}

for NODE_DATA in "${POOL_DATA[@]}"; do
	IFS=" "
	NODE_DATA_ARRAY=(${NODE_DATA})
	NODE_NAME="$(tr '[:lower:]' '[:upper:]' <<< ${NODE_DATA_ARRAY:0:1})${NODE_DATA_ARRAY:1}"
	NODE_NUMBER="${NODE_NAME:(-1)}"
	NODE_IP=${NODE_DATA_ARRAY[1]}
	NODE_PORT=${NODE_DATA_ARRAY[2]}
	CLIENT_PORT=${NODE_DATA_ARRAY[3]}
	
	if [ ! -z "$DEBUG_MESSAGES" ]; then
		echo "------------------------------------------------------------------------"
		echo "Pool data for ${NODE_NAME} ..."
		echo "------------------------------------------------------------------------"
		echo "NODE_DATA=${NODE_DATA}"
		echo "NODE_NAME=${NODE_NAME}"
		echo "NODE_NUMBER=${NODE_NUMBER}"
		echo "NODE_IP=${NODE_IP}"
		echo "NODE_PORT=${NODE_PORT}"
		echo "CLIENT_PORT=${CLIENT_PORT}"
		echo "NODE_IP_LIST=${NODE_IP_LIST}"
		echo "------------------------------------------------------------------------"
		echo
		
		echo "------------------------------------------------------------------------"
		echo "Parameters for call to oc_configure_node_deployment.sh"
		echo "------------------------------------------------------------------------"
		echo "DEPLOYMENT_CONFIG_TEMPLATE: ${DEPLOYMENT_CONFIG_TEMPLATE}"
		echo "DEPLOYMENT_CONFIG_POST_FIX: ${DEPLOYMENT_CONFIG_POST_FIX}"
		echo "SOURCE_IMAGE_NAME: ${SOURCE_IMAGE_NAME}"
		echo "IMAGE_TAG: ${IMAGE_TAG}"
		echo "NODE_IP_LIST: ${NODE_IP_LIST}"
		echo "NODE_COUNT: ${NODE_COUNT}"
		echo "CLIENT_COUNT: ${CLIENT_COUNT}"
		echo "CLIENT_PORT: ${CLIENT_PORT}"
		echo "HOME_DIRECTORY: ${HOME_DIRECTORY}"
		echo "NODE_NAME: ${NODE_NAME}"
		echo "NODE_NUMBER: ${NODE_NUMBER}"
		echo "NODE_PORT: ${NODE_PORT}"
    echo "NODE_SERVICE_HOST_PATTERN=${NODE_SERVICE_HOST_PATTERN}"
		echo "------------------------------------------------------------------------"
		echo
	fi
	
	${SCRIPT_DIR}/oc_configure_node_deployment.sh \
		${DEPLOYMENT_CONFIG_TEMPLATE} \
		${DEPLOYMENT_CONFIG_POST_FIX} \
		${SOURCE_IMAGE_NAME} \
		${IMAGE_TAG} \
		${NODE_IP_LIST} \
		${NODE_COUNT} \
		${CLIENT_COUNT} \
		${CLIENT_PORT} \
		${HOME_DIRECTORY} \
		${NODE_NAME} \
		${NODE_NUMBER} \
		${NODE_PORT} \
    ${NODE_SERVICE_HOST_PATTERN}
done

IFS=${ORIGINAL_IFS}