#!/bin/bash

SCRIPT_DIR=$(dirname $0)

if [ ! -z "${NODE_SERVICE_HOST_PATTERN}" ]; then 
  NEW_NODE_IP_LIST=$(${SCRIPT_DIR}/getNodeAddressList.sh ${NODE_SERVICE_HOST_PATTERN})
  rc=${?}; 
  if [[ ${rc} != 0 ]]; then
    echo "Call to getNodeAddressList.sh failed:"
    echo -e "\t${NEW_NODE_IP_LIST}"
    exit ${rc}; 
  fi

  NEW_NODE_COUNT=$(${SCRIPT_DIR}/getNodeCount.sh ${NEW_NODE_IP_LIST})
  rc=${?}; 
  if [[ ${rc} != 0 ]]; then
    echo "Call to getNodeCount.sh failed:"
    echo -e "\t${NEW_NODE_COUNT}"
    exit ${rc}; 
  fi    

  if [ ! -z "$NEW_NODE_IP_LIST" ]; then
    echo ===============================================================================
    echo "Configuring OpenShift environment ..."
    echo -------------------------------------------------------------------------------
    echo "Changing;"
    echo -e "\tNODE_IP_LIST: ${NODE_IP_LIST}"
    export NODE_IP_LIST=${NEW_NODE_IP_LIST}
    echo -e "\tNODE_IP_LIST: ${NODE_IP_LIST}"
    echo -------------------------------------------------------------------------------
    echo "Changing;"
    echo -e "\tNODE_COUNT: ${NODE_COUNT}"
    export NODE_COUNT=${NEW_NODE_COUNT}
    echo -e "\tNODE_COUNT: ${NODE_COUNT}"
    echo ===============================================================================
    echo
  fi
fi

if [ ! -z "${NODE_NAME}" ] && [ ! -z "${NODE_IP}" ] && [ ! -z "${NODE_PORT}" ] && [ ! -z "${CLIENT_IP}" ] && [ ! -z "${CLIENT_PORT}" ]; then
  echo ===============================================================================
  echo "Initializing indy node:"
  echo -e "\tName: ${NODE_NAME}"
  echo -e "\tNode IP: ${NODE_IP}"
  echo -e "\tNode Port: ${NODE_PORT}"
  echo -e "\tClient IP: ${CLIENT_IP}"
  echo -e "\tClient Port: ${CLIENT_PORT}"
  echo -------------------------------------------------------------------------------
  init_indy_node ${NODE_NAME} ${NODE_IP} ${NODE_PORT} ${CLIENT_IP} ${CLIENT_PORT}
  echo ===============================================================================
  echo
fi 

if [ ! -z "${NODE_COUNT}" ] && [ ! -z "${CLIENT_COUNT}" ] && [ ! -z "${NODE_NUMBER}" ] && [ ! -z "${NODE_IP_LIST}" ]; then 
  echo ===============================================================================
  echo "Generating indy pool transactions for indy node:"
  echo -e "\tNode Count: ${NODE_COUNT}"
  echo -e "\tClient Count: ${CLIENT_COUNT}"
  echo -e "\tNode Number: ${NODE_NUMBER}"
  echo -e "\tNode IP Address List: ${NODE_IP_LIST}"
  echo -------------------------------------------------------------------------------
  generate_indy_pool_transactions --nodes ${NODE_COUNT} --clients ${CLIENT_COUNT} --nodeNum ${NODE_NUMBER} --ips "${NODE_IP_LIST}"; 
  echo ===============================================================================
  echo
fi

if [ -z "${NODE_NUMBER}" ] && [ ! -z "${AGENT_NAME}" ] &&[ ! -z "${NODE_COUNT}" ] && [ ! -z "${CLIENT_COUNT}" ] && [ ! -z "${NODE_IP_LIST}" ]; then 
  echo ===============================================================================
  echo "Generating indy pool transactions for agent node:"
  echo -e "\tAgent Name: ${AGENT_NAME}"
  echo -e "\tNode Count: ${NODE_COUNT}"
  echo -e "\tClient Count: ${CLIENT_COUNT}"
  echo -e "\tNode IP Address List: ${NODE_IP_LIST}"
  echo -------------------------------------------------------------------------------
  generate_indy_pool_transactions --nodes ${NODE_COUNT} --clients ${CLIENT_COUNT} --ips "${NODE_IP_LIST}"; 
  echo ===============================================================================
  echo
fi

if [ -z "${NODE_NUMBER}" ] && [ -z "${AGENT_NAME}" ] &&[ ! -z "${NODE_COUNT}" ] && [ ! -z "${CLIENT_COUNT}" ] && [ ! -z "${NODE_IP_LIST}" ]; then 
  echo ===============================================================================
  echo "Generating indy pool transactions for client node:"
  echo -e "\tNode Count: ${NODE_COUNT}"
  echo -e "\tClient Count: ${CLIENT_COUNT}"
  echo -e "\tNode IP Address List: ${NODE_IP_LIST}"
  echo -------------------------------------------------------------------------------
  generate_indy_pool_transactions --nodes ${NODE_COUNT} --clients ${CLIENT_COUNT} --ips "${NODE_IP_LIST}"; 
  echo ===============================================================================
  echo
fi