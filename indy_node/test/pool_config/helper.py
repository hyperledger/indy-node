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

from stp_core.loop.eventually import eventually
from plenum.test.helper import waitForSufficientRepliesForRequests
from plenum.test import waits as plenumWaits
from indy_client.client.wallet.pool_config import PoolConfig as WPoolConfig
from indy_node.server.pool_config import PoolConfig as SPoolConfig
from indy_node.utils.node_control_tool import NodeControlTool
from indy_common.config_util import getConfig


config = getConfig()


def sendPoolConfig(client, wallet, poolConfigData):
    poolCfg = WPoolConfig(trustee=wallet.defaultId, **poolConfigData)
    wallet.doPoolConfig(poolCfg)
    reqs = wallet.preparePending()
    req = client.submitReqs(*reqs)[0][0]
    return poolCfg, req


def ensurePoolConfigSent(looper, trustee, trusteeWallet, sendPoolCfg):
    poolCfg, req = sendPoolConfig(trustee, trusteeWallet, sendPoolCfg)
    waitForSufficientRepliesForRequests(looper, trustee, requests=[req])

    def check():
        assert trusteeWallet.getPoolConfig(poolCfg.key).seqNo

    timeout = plenumWaits.expectedReqAckQuorumTime()
    looper.run(eventually(check, retryWait=1, timeout=timeout))
    return poolCfg


def checkPoolConfigWritableSet(nodes, writable):
    for node in nodes:
        assert node.poolCfg.isWritable() == writable
