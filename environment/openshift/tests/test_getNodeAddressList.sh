#!/bin/bash
SCRIPT_DIR=$(dirname $0)/..                                                                                                                                            

NODE_SERVICE_HOST_PATTERN="NODE[0-9]+_SERVICE_HOST="
export NODE1_SERVICE_HOST="172.30.220.129"    
export NODE2_SERVICE_HOST="172.30.59.5"
#export NODE3_SERVICE_HOST="172.30.98.46"                                                                                                                            
#export NODE4_SERVICE_HOST="172.30.108.143"
#export NODE40_SERVICE_HOST="172.30.108.143"

NEW_NODE_IP_LIST=$(${SCRIPT_DIR}/scripts/common/getNodeAddressList.sh ${NODE_SERVICE_HOST_PATTERN})
rc=${?}; 
if [[ ${rc} != 0 ]]; then
	echo "Call to getNodeAddressList.sh failed:"
	echo -e "\t${NEW_NODE_IP_LIST}"
	exit ${rc}; 
fi

NEW_NODE_COUNT=$(${SCRIPT_DIR}/scripts/common/getNodeCount.sh ${NEW_NODE_IP_LIST})
rc=${?}; 
if [[ ${rc} != 0 ]]; then
	echo "Call to getNodeCount.sh failed:"
	echo -e "\t${NEW_NODE_COUNT}"
	exit ${rc}; 
fi

if [ -z "$NEW_NODE_IP_LIST" ]; then
	NEW_NODE_IP_LIST="Empty"
fi

echo
echo "NEW_NODE_COUNT: ${NEW_NODE_COUNT}"
echo "NEW_NODE_IP_LIST: ${NEW_NODE_IP_LIST}"
