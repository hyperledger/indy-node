#!/bin/bash

USER_ID="$(id -u)"
SCRIPT_DIR=$(dirname $0)

# ==============================================================================
# Script for setting up the build environment for the Alice example in OpenShift
#
# * Requires the OpenShift Origin CLI
# ------------------------------------------------------------------------------
# Usage on Windows:
#  MSYS_NO_PATHCONV=1 ./oc_configure_builds.sh
# ------------------------------------------------------------------------------
# ToDo:
# * Add support for create or update.
# -----------------------------------------------------------------------------------
#DEBUG_MESSAGES=1
# -----------------------------------------------------------------------------------
PROJECT_NAME="${1}"
GIT_REF="${2}"
GIT_URI="${3}"
GIT_CONTEXT_DIR="${4}"
POOL_DATA_FILE="${5}"
CLIENT_COUNT="${6}"
# -----------------------------------------------------------------------------------
if [ -z "$PROJECT_NAME" ]; then
	PROJECT_NAME="myproject"
	echo "Defaulting 'PROJECT_NAME' to ${PROJECT_NAME} ..."
	echo
fi

if [ -z "$GIT_REF" ]; then
	GIT_REF="stable"
	echo "Defaulting 'GIT_REF' to ${GIT_REF} ..."
	echo
fi

if [ -z "$GIT_URI" ]; then
	GIT_URI="https://github.com/hyperledger/indy-node.git"
	echo "Defaulting 'GIT_URI' to ${GIT_URI} ..."
	echo
fi

if [ -z "$GIT_CONTEXT_DIR" ]; then
	GIT_CONTEXT_DIR="openshift"
	echo "Defaulting 'GIT_CONTEXT_DIR' to ${GIT_CONTEXT_DIR} ..."
	echo
fi

if [ -z "$POOL_DATA_FILE" ]; then
	POOL_DATA_FILE="pool_data"
	echo "Defaulting 'POOL_DATA_FILE' to ${POOL_DATA_FILE} ..."
	echo
fi

if [ -z "$CLIENT_COUNT" ]; then
	CLIENT_COUNT=10
	echo "Defaulting 'CLIENT_COUNT' to ${CLIENT_COUNT} ..."
	echo
fi

if [ ! -z "$MissingParam" ]; then
	echo "============================================"
	echo "One or more parameters are missing!"
	echo "--------------------------------------------"	
	echo "PROJECT_NAME[{1}]: ${1}"
	echo "GIT_REF[{2}]: ${2}"
	echo "GIT_URI[{3}]: ${3}"
	echo "GIT_CONTEXT_DIR[{4}]: ${4}"
	echo "POOL_DATA_FILE[{5}]: ${5}"
	echo "CLIENT_COUNT[{6}]: ${6}"
	echo "============================================"
	echo
	exit 1
fi
# -------------------------------------------------------------------------------------
TEMPLATE_DIR="templates"
BuildConfigTemplate="${SCRIPT_DIR}/${TEMPLATE_DIR}/buildConfig.json"
BuildConfigPostfix="_BuildConfig.json"

IndyBaseBuildConfig="indyBase${BuildConfigPostfix}"
IndyCoreBuildConfig="indyCore${BuildConfigPostfix}"
IndyNodeBuildConfig="indyNode${BuildConfigPostfix}"
IndyClientBuildConfig="indyClient${BuildConfigPostfix}"
IndyAgentBuildConfig="indyAgent${BuildConfigPostfix}"

IndyBaseDockerFile="base.systemd.ubuntu.dockerfile"
IndyCoreDockerFile="core.ubuntu.dockerfile"
IndyNodeDockerFile="node.init.ubuntu.dockerfile"
IndyClientDockerFile="client.ubuntu.dockerfile"
IndyAgentDockerFile="agent.ubuntu.dockerfile"

IndyBaseName="indybase"
IndyCoreName="indycore"
IndyNodeName="indynode"
IndyClientName="indyclient"
IndyAgentName="indyagent"

IndyAgentInstanceName="Faber"
IndyAgentInstancePort="5555"

IndyBaseSourceImageKind="DockerImage"
IndyCoreSourceImageKind="ImageStreamTag"
IndyNodeSourceImageKind="ImageStreamTag"
IndyClientSourceImageKind="ImageStreamTag"
IndyAgentSourceImageKind="ImageStreamTag"

IndyBaseSourceImageName="solita/ubuntu-systemd"
IndyCoreSourceImageName="indybase"
IndyNodeSourceImageName="indycore"
IndyClientSourceImageName="indycore"
IndyAgentSourceImageName="indycore"

OutputImageTag="latest"
IndyBaseSourceImageTag="16.04"
IndyCoreSourceImageTag="${OutputImageTag}"
IndyNodeSourceImageTag="${OutputImageTag}"
IndyClientSourceImageTag="${OutputImageTag}"
IndyAgentSourceImageTag="${OutputImageTag}"
# ==============================================================================

echo "============================================================================="
echo "Switching to project ${PROJECT_NAME} ..."
echo "-----------------------------------------------------------------------------"
oc project ${PROJECT_NAME}
echo "============================================================================"
echo 


echo "============================================================================="
echo "Deleting previous build configuration files ..."
echo "-----------------------------------------------------------------------------"
for file in *_BuildConfig.json; do 
	echo "Deleting ${file} ..."
	rm -rf ${file};
done
echo "============================================================================="
echo

echo "============================================================================="
echo "Generating base build configuration ..."
echo "-----------------------------------------------------------------------------"
${SCRIPT_DIR}/oc_configure_base_build.sh \
	${BuildConfigTemplate} \
	${BuildConfigPostfix} \
	${IndyBaseName} \
	${IndyBaseSourceImageKind} \
	${IndyBaseSourceImageName} \
	${IndyBaseSourceImageTag} \
	${IndyBaseDockerFile} \
	${GIT_CONTEXT_DIR} \
	${GIT_REF} \
	${GIT_URI} \
	${IndyBaseName} \
	${OutputImageTag} \	
echo "============================================================================="
echo

echo "============================================================================="
echo "Generating core build configuration ..."
echo "-----------------------------------------------------------------------------"
${SCRIPT_DIR}/oc_configure_base_build.sh \
	${BuildConfigTemplate} \
	${BuildConfigPostfix} \
	${IndyCoreName} \
	${IndyCoreSourceImageKind} \
	${IndyCoreSourceImageName} \
	${IndyCoreSourceImageTag} \
	${IndyCoreDockerFile} \
	${GIT_CONTEXT_DIR} \
	${GIT_REF} \
	${GIT_URI} \
	${IndyCoreName} \
	${OutputImageTag} \	
echo "============================================================================="
echo

echo "============================================================================="
echo "Generating node pool data ..."
echo "-----------------------------------------------------------------------------"
${SCRIPT_DIR}/generatePoolData.sh ${POOL_DATA_FILE}
echo "============================================================================="
echo

echo "============================================================================="
echo "Generating node build configuration ..."
echo "-----------------------------------------------------------------------------"
NODE_DATA=$(${SCRIPT_DIR}/getNodeInfoFromPool.sh ${POOL_DATA_FILE})
NODE_NAME=$(${SCRIPT_DIR}/getNodeInfo.sh "${NODE_DATA}" "name")
NODE_NUMBER=$(${SCRIPT_DIR}/getNodeInfo.sh "${NODE_DATA}" "number")
NODE_IP=$(${SCRIPT_DIR}/getNodeInfo.sh "${NODE_DATA}" "ip")
NODE_PORT=$(${SCRIPT_DIR}/getNodeInfo.sh "${NODE_DATA}" "nodeport")
CLIENT_PORT=$(${SCRIPT_DIR}/getNodeInfo.sh "${NODE_DATA}" "clientport")

NODE_IP_LIST=$(${SCRIPT_DIR}/getNodeAddressListFromPool.sh ${POOL_DATA_FILE})
NODE_COUNT=$(${SCRIPT_DIR}/getNodeCount.sh ${NODE_IP_LIST})

if [ ! -z "$DEBUG_MESSAGES" ]; then
	echo "------------------------------------------------------------------------"
	echo "Parsed pool data for ${NODE_NAME} ..."
	echo "------------------------------------------------------------------------"
	echo "NODE_DATA=${NODE_DATA}"
	echo "NODE_NAME=${NODE_NAME}"
	echo "NODE_NUMBER=${NODE_NUMBER}"
	echo "NODE_IP=${NODE_IP}"
	echo "NODE_PORT=${NODE_PORT}"
	echo "CLIENT_PORT=${CLIENT_PORT}"
	echo
	echo "NODE_IP_LIST=${NODE_IP_LIST}"
	echo "NODE_COUNT=${NODE_COUNT}"
	echo "------------------------------------------------------------------------"
	echo
fi

${SCRIPT_DIR}/oc_configure_node_build.sh \
	${BuildConfigTemplate} \
	${BuildConfigPostfix} \
	${IndyNodeName} \
	${IndyNodeSourceImageKind} \
	${IndyNodeSourceImageName} \
	${IndyNodeSourceImageTag} \
	${IndyNodeDockerFile} \
	${GIT_CONTEXT_DIR} \
	${GIT_REF} \
	${GIT_URI} \
	${IndyNodeName} \
	${OutputImageTag} \
	${NODE_NAME} \
	${NODE_PORT} \
	${CLIENT_PORT} \
	${NODE_IP_LIST} \
	${NODE_COUNT} \
	${CLIENT_COUNT} \
	${NODE_NUMBER}
echo "============================================================================="
echo

echo "============================================================================="
echo "Generating client build configuration ..."
echo "-----------------------------------------------------------------------------"
${SCRIPT_DIR}/oc_configure_client_build.sh \
	${BuildConfigTemplate} \
	${BuildConfigPostfix} \
	${IndyClientName} \
	${IndyClientSourceImageKind} \
	${IndyClientSourceImageName} \
	${IndyClientSourceImageTag} \
	${IndyClientDockerFile} \
	${GIT_CONTEXT_DIR} \
	${GIT_REF} \
	${GIT_URI} \
	${IndyClientName} \
	${OutputImageTag} \
	${NODE_IP_LIST} \
	${NODE_COUNT} \
	${CLIENT_COUNT}
echo "============================================================================="
echo

echo "============================================================================="
echo "Generating agent build configuration ..."
echo "-----------------------------------------------------------------------------"
${SCRIPT_DIR}/oc_configure_agent_build.sh \
	${BuildConfigTemplate} \
	${BuildConfigPostfix} \
	${IndyAgentName} \
	${IndyAgentSourceImageKind} \
	${IndyAgentSourceImageName} \
	${IndyAgentSourceImageTag} \
	${IndyAgentDockerFile} \
	${GIT_CONTEXT_DIR} \
	${GIT_REF} \
	${GIT_URI} \
	${IndyAgentName} \
	${OutputImageTag} \
	${NODE_IP_LIST} \
	${NODE_COUNT} \
	${CLIENT_COUNT} \
	${IndyAgentInstanceName} \
	${IndyAgentInstancePort}

echo "============================================================================="
echo

echo "============================================================================="
echo "Cleaning out existing OpenShift resources ..."
echo "============================================================================"
oc delete imagestreams,bc --all
echo

echo "============================================================================="
echo "Creating build configurations in OpenShift project; ${PROJECT_NAME} ..."
echo "============================================================================="
for file in *_BuildConfig.json; do 
	echo "Loading ${file} ...";
	oc create -f ${file};
	echo;
done
echo
