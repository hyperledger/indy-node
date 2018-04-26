from stp_core.loop.eventually import eventually
from plenum.test.helper import waitForSufficientRepliesForRequests
from plenum.test import waits as plenumWaits
from indy_client.client.wallet.pool_config import PoolConfig as WPoolConfig


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
