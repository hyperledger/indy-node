from indy_client.test.helper import getClientAddedWithRole
from indy_client.test.helper import checkRejects, checkNacks
from stp_core.loop.eventually import eventually
from indy_node.test.pool_config.helper import sendPoolConfig
from plenum.common.constants import STEWARD


def test_only_trustee_send_pool_config_writes_true_force_false(
        nodeSet, tdirWithClientPoolTxns, looper, trustee, trusteeWallet, poolConfigWTFF):
    stClient, stWallet = getClientAddedWithRole(
        nodeSet, tdirWithClientPoolTxns, looper, trustee, trusteeWallet, 'tmpname', STEWARD)
    _, req = sendPoolConfig(stClient, stWallet, poolConfigWTFF)
    looper.run(eventually(checkRejects, stClient, req.reqId, 'cannot do'))


def test_only_trustee_send_pool_config_writes_false_force_false(
        nodeSet, tdirWithClientPoolTxns, looper, trustee, trusteeWallet, poolConfigWFFF):
    stClient, stWallet = getClientAddedWithRole(
        nodeSet, tdirWithClientPoolTxns, looper, trustee, trusteeWallet, 'tmpname', STEWARD)
    _, req = sendPoolConfig(stClient, stWallet, poolConfigWFFF)
    looper.run(eventually(checkRejects, stClient, req.reqId, 'cannot do'))


def test_only_trustee_send_pool_config_writes_true_force_true(
        nodeSet, tdirWithClientPoolTxns, looper, trustee, trusteeWallet, poolConfigWTFT):
    stClient, stWallet = getClientAddedWithRole(
        nodeSet, tdirWithClientPoolTxns, looper, trustee, trusteeWallet, 'tmpname', STEWARD)
    _, req = sendPoolConfig(stClient, stWallet, poolConfigWTFT)
    looper.run(eventually(checkNacks, stClient, req.reqId, 'cannot do'))


def test_only_trustee_send_pool_config_writes_false_force_true(
        nodeSet, tdirWithClientPoolTxns, looper, trustee, trusteeWallet, poolConfigWFFT):
    stClient, stWallet = getClientAddedWithRole(
        nodeSet, tdirWithClientPoolTxns, looper, trustee, trusteeWallet, 'tmpname', STEWARD)
    _, req = sendPoolConfig(stClient, stWallet, poolConfigWFFT)
    looper.run(eventually(checkNacks, stClient, req.reqId, 'cannot do'))
