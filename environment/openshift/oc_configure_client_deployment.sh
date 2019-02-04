#!/bin/bash

USER_ID="$(id -u)"
SCRIPT_DIR=$(dirname $0)

# ===========================================================================
# Generate a Client Deployment Configuration
# ===========================================================================
DEPLOYMENT_CONFIG_TEMPLATE="${1}"
DEPLOYMENT_CONFIG_POST_FIX="${2}"
SOURCE_IMAGE_NAME="${3}"
IMAGE_TAG="${4}"
NODE_IP_LIST="${5}"
NODE_COUNT="${6}"
CLIENT_COUNT="${7}"
HOME_DIRECTORY="${8}"
CLIENT_NAME="${9}"
NODE_SERVICE_HOST_PATTERN="${10}"
# -----------------------------------------------------------------------------------
#DEBUG_MESSAGES=1
# -----------------------------------------------------------------------------------
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

if [ -z "$NODE_COUNT" ]; then
	echo "You must supply NODE_COUNT."
	MissingParam=1
fi

if [ -z "$CLIENT_COUNT" ]; then
	echo "You must supply CLIENT_COUNT."
	MissingParam=1
fi

if [ -z "$HOME_DIRECTORY" ]; then
	echo "You must supply HOME_DIRECTORY."
	MissingParam=1
fi

if [ -z "$CLIENT_NAME" ]; then
	echo "You must supply CLIENT_NAME."
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
	echo "DEPLOYMENT_CONFIG_TEMPLATE[{1}]: ${1}"
	echo "DEPLOYMENT_CONFIG_POST_FIX[{2}]: ${2}"
	echo "SOURCE_IMAGE_NAME[{3}]: ${3}"
	echo "IMAGE_TAG[{4}]: ${4}"
	echo "NODE_IP_LIST[{5}]: ${5}"
	echo "NODE_COUNT[{6}]: ${6}"
	echo "CLIENT_COUNT[{7}]: ${7}"
	echo "HOME_DIRECTORY[{8}]: ${8}"
	echo "CLIENT_NAME[{9}]: ${9}"
	echo "NODE_SERVICE_HOST_PATTERN[{10}]: ${10}"
	echo "============================================"
	echo
	exit 1
fi
# -----------------------------------------------------------------------------------
ApplicationName="$(echo "$CLIENT_NAME" | tr '[:upper:]' '[:lower:]')-client"
ServiceDescription="Exposes and load balances the pods for the ${CLIENT_NAME} client."
ApplicationHostName=""
ImageNamespace=""
DeploymentConfig="${ApplicationName}${DEPLOYMENT_CONFIG_POST_FIX}"
# ===================================================================================

echo "Generating deployment configuration file for the ${CLIENT_NAME} client..."

if [ ! -z "$DEBUG_MESSAGES" ]; then
	echo
	echo "------------------------------------------------------------------------"
	echo "Parameters for call to 'oc process' for the ${CLIENT_NAME} client..."
	echo "------------------------------------------------------------------------"
	echo "Template=${DEPLOYMENT_CONFIG_TEMPLATE}"
	echo "APPLICATION_NAME=${ApplicationName}"
	echo "APPLICATION_SERVICE_DESCRIPTION=${ServiceDescription}"
	echo "APPLICATION_HOSTNAME=${ApplicationHostName}"
	echo "SOURCE_IMAGE_NAME=${SOURCE_IMAGE_NAME}"
	echo "IMAGE_NAMESPACE=${ImageNamespace}"
	echo "DEPLOYMENT_TAG=${IMAGE_TAG}"
	echo "NODE_IP_LIST=${NODE_IP_LIST}"
	echo "NODE_COUNT=${NODE_COUNT}"
	echo "CLIENT_COUNT=${CLIENT_COUNT}"
	echo "HOME_DIR=${HOME_DIRECTORY}"
  echo "NODE_SERVICE_HOST_PATTERN=${NODE_SERVICE_HOST_PATTERN}"
	echo "Output File=${DeploymentConfig}"
	echo "------------------------------------------------------------------------"
	echo
fi

oc process \
-f ${DEPLOYMENT_CONFIG_TEMPLATE} \
-p APPLICATION_NAME=${ApplicationName} \
-p APPLICATION_SERVICE_DESCRIPTION="${ServiceDescription}" \
-p APPLICATION_HOSTNAME=${ApplicationHostName} \
-p SOURCE_IMAGE_NAME=${SOURCE_IMAGE_NAME} \
-p IMAGE_NAMESPACE=${ImageNamespace} \
-p DEPLOYMENT_TAG=${IMAGE_TAG} \
-p NODE_IP_LIST=${NODE_IP_LIST} \
-p NODE_COUNT=${NODE_COUNT} \
-p CLIENT_COUNT=${CLIENT_COUNT} \
-p HOME_DIR=${HOME_DIRECTORY} \
-p NODE_SERVICE_HOST_PATTERN=${NODE_SERVICE_HOST_PATTERN} \
> ${DeploymentConfig}
echo "Generated ${DeploymentConfig} ..."
echo
