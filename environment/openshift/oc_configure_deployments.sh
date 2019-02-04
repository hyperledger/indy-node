#!/bin/bash

USER_ID="$(id -u)"
SCRIPT_DIR=$(dirname $0)

# =====================================================================================
# Script for setting up the deployment environment for the Alice example in OpenShift
# * Requires the OpenShift Origin CLI
# -------------------------------------------------------------------------------------
# Usage on Windows:
#  * MSYS_NO_PATHCONV=1 ./oc_configure_deployments.sh
# -------------------------------------------------------------------------------------
# ToDo:
# * Add support for create or update.
# -----------------------------------------------------------------------------------
#DEBUG_MESSAGES=1
# -----------------------------------------------------------------------------------
PROJECT_NAME="${1}"
POOL_DATA_FILE="${2}"
CLIENT_COUNT="${3}"
# -----------------------------------------------------------------------------------
if [ -z "$PROJECT_NAME" ]; then
	PROJECT_NAME="myproject"
	echo "Defaulting 'PROJECT_NAME' to ${PROJECT_NAME} ..."
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
	echo "POOL_DATA_FILE[{2}]: ${2}"
	echo "CLIENT_COUNT[{3}]: ${3}"
	echo "============================================"
	echo
	exit 1
fi
# -------------------------------------------------------------------------------------
TEMPLATE_DIR="templates"
DeploymentConfigTemplate="${SCRIPT_DIR}/${TEMPLATE_DIR}/deploymentConfig.json"
DeploymentConfigPostfix="_DeploymentConfig.json"
IndyHomeDirectory="/home/indy"

ClientImageName="indyclient"
NodeImageName="indynode"
AgentImageName="indyagent"
ImageTag="latest"

NodeName="Node"
ClientName="Cli"

FaberAgentName="Faber"
FaberAgentPort="5555"

AcmeAgentName="Acme"
AcmeAgentPort="6666"

ThriftAgentName="Thrift"
ThriftAgentPort="7777"
# -------------------------------------------------------------------------------------
NODE_IP_LIST=$(${SCRIPT_DIR}/getNodeAddressListFromPool.sh ${POOL_DATA_FILE})
NODE_COUNT=$(${SCRIPT_DIR}/getNodeCount.sh ${NODE_IP_LIST})

NODE_DATA=$(${SCRIPT_DIR}/getNodeInfoFromPool.sh ${POOL_DATA_FILE})
BASE_NODE_NAME=$(${SCRIPT_DIR}/getNodeInfo.sh "${NODE_DATA}" "basename")
BASE_NODE_NAME="$(echo "$BASE_NODE_NAME" | tr '[:lower:]' '[:upper:]')"
NODE_SERVICE_HOST_PATTERN="${BASE_NODE_NAME}[0-9]+_SERVICE_HOST="
# =====================================================================================

echo "============================================================================="
echo "Switching to project ${PROJECT_NAME} ..."
echo "-----------------------------------------------------------------------------"
oc project ${PROJECT_NAME}
echo "============================================================================"
echo 

echo "============================================================================="
echo "Deleting previous deployment configuration files ..."
echo "-----------------------------------------------------------------------------"
for file in *${DeploymentConfigPostfix}; do
	echo "Deleting ${file} ..."
	rm -rf ${file};
done
echo "============================================================================="
echo

# ===========================================================================
# Node Deployment Configurations
# ===========================================================================
echo "============================================================================="
echo "Generating node deployment configuration(s) ..."
echo "-----------------------------------------------------------------------------"
${SCRIPT_DIR}/oc_configure_node_deployments.sh \
	${POOL_DATA_FILE} \
	${CLIENT_COUNT} \
	${DeploymentConfigTemplate} \
	${DeploymentConfigPostfix} \
	${NodeImageName} \
	${ImageTag} \
	${NODE_IP_LIST} \
	${IndyHomeDirectory} \
	${NODE_SERVICE_HOST_PATTERN}
echo "============================================================================="
echo
# ===========================================================================

# ===========================================================================
# Client Deployment Configuration(s)
# ===========================================================================
echo "============================================================================="
echo "Generating client deployment configuration(s) ..."
echo "-----------------------------------------------------------------------------"
${SCRIPT_DIR}/oc_configure_client_deployment.sh \
	${DeploymentConfigTemplate} \
	${DeploymentConfigPostfix} \
	${ClientImageName} \
	${ImageTag} \
	${NODE_IP_LIST} \
	${NODE_COUNT} \
	${CLIENT_COUNT} \
	${IndyHomeDirectory} \
	${ClientName} \
	${NODE_SERVICE_HOST_PATTERN}
echo "============================================================================="
echo
# ===========================================================================

# ===========================================================================
# Sovin Agent Deployment Configuration(s)
# ---------------------------------------------------------------------------
# ToDo:
# * Get this information from a list like the nodes with pool_data.
# ===========================================================================
echo "============================================================================="
echo "Generating agent deployment configuration(s) ..."
echo "-----------------------------------------------------------------------------"
${SCRIPT_DIR}/oc_configure_agent_deployment.sh \
	${DeploymentConfigTemplate} \
	${DeploymentConfigPostfix} \
	${AgentImageName} \
	${ImageTag} \
	${NODE_IP_LIST} \
	${NODE_COUNT} \
	${CLIENT_COUNT} \
	${IndyHomeDirectory} \
	${FaberAgentName} \
	${FaberAgentPort} \
	${NODE_SERVICE_HOST_PATTERN}

 
${SCRIPT_DIR}/oc_configure_agent_deployment.sh \
	${DeploymentConfigTemplate} \
	${DeploymentConfigPostfix} \
	${AgentImageName} \
	${ImageTag} \
	${NODE_IP_LIST} \
	${NODE_COUNT} \
	${CLIENT_COUNT} \
	${IndyHomeDirectory} \
	${AcmeAgentName} \
	${AcmeAgentPort} \
	${NODE_SERVICE_HOST_PATTERN}

${SCRIPT_DIR}/oc_configure_agent_deployment.sh \
	${DeploymentConfigTemplate} \
	${DeploymentConfigPostfix} \
	${AgentImageName} \
	${ImageTag} \
	${NODE_IP_LIST} \
	${NODE_COUNT} \
	${CLIENT_COUNT} \
	${IndyHomeDirectory} \
	${ThriftAgentName} \
	${ThriftAgentPort} \
	${NODE_SERVICE_HOST_PATTERN}	
echo "============================================================================="
echo
# ===========================================================================

echo "============================================================================="
echo "Cleaning out all existing OpenShift resources ..."
echo "-----------------------------------------------------------------------------"
oc delete routes,services,dc --all
echo "============================================================================="
echo

echo "============================================================================="
echo "Creating deployment configurations in OpenShift project; ${PROJECT_NAME} ..."
echo "-----------------------------------------------------------------------------"
for file in *${DeploymentConfigPostfix}; do 
	echo "Loading ${file} ...";
	oc create -f ${file};
	echo;
done
echo "============================================================================="
echo
