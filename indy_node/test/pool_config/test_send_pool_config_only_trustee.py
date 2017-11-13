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

from indy_client.test.helper import getClientAddedWithRole
from indy_client.test.helper import checkRejects, checkNacks
from stp_core.loop.eventually import eventually
from indy_node.test.pool_config.helper import ensurePoolConfigSent, checkPoolConfigWritableSet, sendPoolConfig
from plenum.common.constants import STEWARD


def test_only_trustee_send_pool_config_writes_true_force_false(
        nodeSet, tdir, looper, trustee, trusteeWallet, poolConfigWTFF):
    stClient, stWallet = getClientAddedWithRole(
        nodeSet, tdir, looper, trustee, trusteeWallet, 'tmpname', STEWARD)
    _, req = sendPoolConfig(stClient, stWallet, poolConfigWTFF)
    looper.run(eventually(checkRejects, stClient, req.reqId, 'cannot do'))


def test_only_trustee_send_pool_config_writes_false_force_false(
        nodeSet, tdir, looper, trustee, trusteeWallet, poolConfigWFFF):
    stClient, stWallet = getClientAddedWithRole(
        nodeSet, tdir, looper, trustee, trusteeWallet, 'tmpname', STEWARD)
    _, req = sendPoolConfig(stClient, stWallet, poolConfigWFFF)
    looper.run(eventually(checkRejects, stClient, req.reqId, 'cannot do'))


def test_only_trustee_send_pool_config_writes_true_force_true(
        nodeSet, tdir, looper, trustee, trusteeWallet, poolConfigWTFT):
    stClient, stWallet = getClientAddedWithRole(
        nodeSet, tdir, looper, trustee, trusteeWallet, 'tmpname', STEWARD)
    _, req = sendPoolConfig(stClient, stWallet, poolConfigWTFT)
    looper.run(eventually(checkNacks, stClient, req.reqId, 'cannot do'))


def test_only_trustee_send_pool_config_writes_false_force_true(
        nodeSet, tdir, looper, trustee, trusteeWallet, poolConfigWFFT):
    stClient, stWallet = getClientAddedWithRole(
        nodeSet, tdir, looper, trustee, trusteeWallet, 'tmpname', STEWARD)
    _, req = sendPoolConfig(stClient, stWallet, poolConfigWFFT)
    looper.run(eventually(checkNacks, stClient, req.reqId, 'cannot do'))
