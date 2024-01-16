#!/bin/bash -eu

# Copyright 2018 ConsenSys AG.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

NO_LOCK_REQUIRED=false

. ./.env
source "$(dirname "$0")/common.sh"
dots=""
maxRetryCount=50
HOST=${DOCKER_PORT_2375_TCP_ADDR:-"localhost"}

# Displays links to exposed services
echo "*************************************"
echo "Localnet "
echo "*************************************"

echo "----------------------------------"
echo "List endpoints and services"
echo "----------------------------------"

echo "JSON-RPC HTTP service endpoint                 : http://${HOST}:8545"
echo "JSON-RPC WebSocket service endpoint            : ws://${HOST}:8546"
if [ ! -z `docker compose -f docker-compose.yml ps -q blockscout 2> /dev/null` ]; then
echo "Blockscout address                             : http://${HOST}:26000/"
fi
if [ ! -z `docker compose -f docker-compose.yml ps -q prometheus 2> /dev/null` ]; then
echo "Prometheus address                             : http://${HOST}:9090/graph"
fi
grafana_url="http://${HOST}:3000/d/a1lVy7ycin9Yv/goquorum-overview?orgId=1&refresh=10s&from=now-30m&to=now&var-system=All"
grafana_loki_url="http://${HOST}:3000/d/Ak6eXLsPxFemKYKEXfcH/quorum-logs-loki?orgId=1&var-app=quorum&var-search="
if [[ ! -z `docker ps -q --filter 'label=consensus=besu' 2> /dev/null ` ]]; then
grafana_url="http://${HOST}:3000/d/XE4V0WGZz/besu-overview?orgId=1&refresh=10s&from=now-30m&to=now&var-system=All"
grafana_loki_url="http://${HOST}:3000/d/Ak6eXLsPxFemKYKEXfcH/quorum-logs-loki?orgId=1&var-app=besu&var-search="
fi
if [ ! -z `docker compose -f docker-compose.yml ps -q grafana 2> /dev/null` ]; then
echo "Grafana address                                : $grafana_url"
echo "Collated logs using Grafana and Loki           : $grafana_loki_url"
fi

echo ""
echo "For more information on the endpoints and services, refer to README.md in the installation directory."
echo "****************************************************************"
