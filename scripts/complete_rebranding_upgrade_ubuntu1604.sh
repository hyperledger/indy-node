#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

#!/bin/bash -x

# This script is intended to be used by rebranding upgrade

systemctl stop sovrin-node-control

NODE_SERVICE_ENABLEMENT_STATUS=$(systemctl is-enabled sovrin-node.service)

systemctl disable sovrin-node.service
rm /etc/systemd/system/sovrin-node.service

# Just in case disable sovrin-node-control service (it might be enabled accidentally)
# Normally it was a dependency of sovrin-node service which was the only one enabled
systemctl disable sovrin-node-control.service

rm /etc/systemd/system/sovrin-node-control.service

systemctl daemon-reload
systemctl reset-failed

echo "Starting indy-node"
systemctl start indy-node
# indy-node-control is also started because indy-node requires it

if [ $NODE_SERVICE_ENABLEMENT_STATUS != "disabled" ]; then
    echo "Enable indy-node.service"
    systemctl enable indy-node.service
fi
