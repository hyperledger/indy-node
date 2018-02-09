#!/bin/bash
SCRIPT_DIR=$(dirname $0)

$SCRIPT_DIR/initialize.sh

agentName="$(echo "$AGENT_NAME" | tr '[:upper:]' '[:lower:]')"

# Examples:
# /usr/bin/env python3 /usr/local/lib/python3.5/dist-packages/indy_client/test/agent/faber.py --port 5555 > faber.log
# /usr/bin/env python3 /usr/local/lib/python3.5/dist-packages/indy_client/test/agent/acme.py --port 6666 > acme.log
# /usr/bin/env python3 /usr/local/lib/python3.5/dist-packages/indy_client/test/agent/thrift.py --port 7777 > thrift.log

echo "Starting ${AGENT_NAME} agent node ..."
echo "/usr/bin/env python3 /usr/local/lib/python3.5/dist-packages/indy_client/test/agent/${agentName}.py --port ${AGENT_PORT} > ${agentName}.log"
echo
exec /usr/bin/env python3 /usr/local/lib/python3.5/dist-packages/indy_client/test/agent/${agentName}.py --port ${AGENT_PORT} > ${agentName}.log