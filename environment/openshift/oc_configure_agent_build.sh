#!/bin/bash

USER_ID="$(id -u)"
SCRIPT_DIR=$(dirname $0)

# ===========================================================================
# Generate an Agent Build Configuration
# ===========================================================================
BUILD_CONFIG_TEMPLATE=${1}
BUILD_CONFIG_POST_FIX=${2}
BUILD_NAME=${3}
SOURCE_IMAGE_KIND=${4}
SOURCE_IMAGE_NAME=${5}
SOURCE_IMAGE_TAG=${6}
DOCKER_FILE_PATH=${7}
SOURCE_CONTEXT_DIR=${8}
GIT_REF=${9}
GIT_URI=${10}
OUTPUT_IMAGE_NAME=${11}
OUTPUT_IMAGE_TAG=${12}
NODE_IP_LIST=${13}
NODE_COUNT=${14}
CLIENT_COUNT=${15}
AGENT_NAME=${16}
AGENT_PORT=${17}
# -----------------------------------------------------------------------------------
#DEBUG_MESSAGES=1
# -----------------------------------------------------------------------------------
if [ -z "$BUILD_CONFIG_TEMPLATE" ]; then
	echo "You must supply BUILD_CONFIG_TEMPLATE."
	MissingParam=1
fi

if [ -z "$BUILD_CONFIG_POST_FIX" ]; then
	echo "You must supply BUILD_CONFIG_POST_FIX."
	MissingParam=1
fi

if [ -z "$BUILD_NAME" ]; then
	echo "You must supply BUILD_NAME."
	MissingParam=1
fi

if [ -z "$SOURCE_IMAGE_KIND" ]; then
	echo "You must supply SOURCE_IMAGE_KIND."
	MissingParam=1
fi

if [ -z "$SOURCE_IMAGE_NAME" ]; then
	echo "You must supply SOURCE_IMAGE_NAME."
	MissingParam=1
fi

if [ -z "$SOURCE_IMAGE_TAG" ]; then
	echo "You must supply SOURCE_IMAGE_TAG."
	MissingParam=1
fi

if [ -z "$DOCKER_FILE_PATH" ]; then
	echo "You must supply DOCKER_FILE_PATH."
	MissingParam=1
fi

if [ -z "$SOURCE_CONTEXT_DIR" ]; then
	echo "You must supply SOURCE_CONTEXT_DIR."
	MissingParam=1
fi

if [ -z "$GIT_REF" ]; then
	echo "You must supply GIT_REF."
	MissingParam=1
fi

if [ -z "$GIT_URI" ]; then
	echo "You must supply GIT_URI."
	MissingParam=1
fi

if [ -z "$OUTPUT_IMAGE_NAME" ]; then
	echo "You must supply OUTPUT_IMAGE_NAME."
	MissingParam=1
fi

if [ -z "$OUTPUT_IMAGE_TAG" ]; then
	echo "You must supply OUTPUT_IMAGE_TAG."
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

if [ -z "$AGENT_NAME" ]; then
	echo "You must supply AGENT_NAME."
	MissingParam=1
fi

if [ -z "$AGENT_PORT" ]; then
	echo "You must supply AGENT_PORT."
	MissingParam=1
fi

if [ ! -z "$MissingParam" ]; then
	echo "============================================"
	echo "One or more parameters are missing!"
	echo "--------------------------------------------"	
	echo "BUILD_CONFIG_TEMPLATE[{1}]: ${1}"
	echo "BUILD_CONFIG_POST_FIX[{2}]: ${2}"
	echo "BUILD_NAME[{3}]: ${3}"
	echo "SOURCE_IMAGE_KIND[{4}]: ${4}"
	echo "SOURCE_IMAGE_NAME[{5}]: ${5}"
	echo "SOURCE_IMAGE_TAG[{6}]: ${6}"
	echo "DOCKER_FILE_PATH[{7}]: ${7}"
	echo "SOURCE_CONTEXT_DIR[{8}]: ${8}"
	echo "GIT_REF[{9}]: ${9}"
	echo "GIT_URI[{10}]: ${10}"
	echo "OUTPUT_IMAGE_NAME[{11}]: ${11}"
	echo "OUTPUT_IMAGE_TAG[{12}]: ${12}"	
	echo "NODE_IP_LIST[{13}]: ${13}"
	echo "NODE_COUNT[{14}]: ${14}"
	echo "CLIENT_COUNT[{15}]: ${15}"
	echo "AGENT_NAME[{16}]: ${16}"
	echo "AGENT_PORT[{17}]: ${17}"
    echo "============================================"
	echo
	exit 1
fi
# -----------------------------------------------------------------------------------
BuildConfig=${BUILD_NAME}${BUILD_CONFIG_POST_FIX}
# ===================================================================================

echo "Generating build configuration file for the ${BUILD_NAME} build ..."

if [ ! -z "$DEBUG_MESSAGES" ]; then
	echo
	echo "------------------------------------------------------------------------"
	echo "Parameters for call to 'oc process' for the ${BUILD_NAME} build ..."
	echo "------------------------------------------------------------------------"
	echo "Template=${BUILD_CONFIG_TEMPLATE}"
	echo "BUILD_NAME=${BUILD_NAME}"
	echo "SOURCE_IMAGE_KIND=${SOURCE_IMAGE_KIND}"
	echo "SOURCE_IMAGE_NAME=${SOURCE_IMAGE_NAME}"
	echo "SOURCE_IMAGE_TAG=${SOURCE_IMAGE_TAG}"
	echo "DOCKER_FILE_PATH=${DOCKER_FILE_PATH}"
	echo "SOURCE_CONTEXT_DIR=${SOURCE_CONTEXT_DIR}"
	echo "GIT_REF=${GIT_REF}"
	echo "GIT_URI=${GIT_URI}"
	echo "OUTPUT_IMAGE_NAME=${OUTPUT_IMAGE_NAME}"
	echo "OUTPUT_IMAGE_TAG=${OUTPUT_IMAGE_TAG}"
	echo "INDY_NODE_IP_LIST=${NODE_IP_LIST}"
	echo "INDY_NODE_COUNT=${NODE_COUNT}"
	echo "INDY_CLIENT_COUNT=${CLIENT_COUNT}"
	echo "INDY_AGENT_NAME=${AGENT_NAME}"
	echo "INDY_AGENT_PORT=${AGENT_PORT}"
	echo "Output File=${BuildConfig}"
	echo "------------------------------------------------------------------------"
	echo
fi

oc process \
-f ${BUILD_CONFIG_TEMPLATE} \
-p BUILD_NAME=${BUILD_NAME} \
-p SOURCE_IMAGE_KIND=${SOURCE_IMAGE_KIND} \
-p SOURCE_IMAGE_NAME=${SOURCE_IMAGE_NAME} \
-p SOURCE_IMAGE_TAG=${SOURCE_IMAGE_TAG} \
-p DOCKER_FILE_PATH=${DOCKER_FILE_PATH} \
-p SOURCE_CONTEXT_DIR=${SOURCE_CONTEXT_DIR} \
-p GIT_REF=${GIT_REF} \
-p GIT_URI=${GIT_URI} \
-p OUTPUT_IMAGE_NAME=${OUTPUT_IMAGE_NAME} \
-p OUTPUT_IMAGE_TAG=${OUTPUT_IMAGE_TAG} \
-p INDY_NODE_IP_LIST=${NODE_IP_LIST} \
-p INDY_NODE_COUNT=${NODE_COUNT} \
-p INDY_CLIENT_COUNT=${CLIENT_COUNT} \
-p INDY_AGENT_NAME=${AGENT_NAME} \
-p INDY_AGENT_PORT=${AGENT_PORT} \
> ${BuildConfig}
echo "Generated ${BuildConfig} ..."
echo
