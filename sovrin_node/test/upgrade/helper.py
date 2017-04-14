from stp_core.loop.eventually import eventually
from plenum.test.helper import waitForSufficientRepliesForRequests
from sovrin_client.client.wallet.upgrade import Upgrade
from sovrin_node.server.upgrader import Upgrader


def sendUpgrade(client, wallet, upgradeData):
    upgrade = Upgrade(**upgradeData, trustee=wallet.defaultId)
    wallet.doPoolUpgrade(upgrade)
    reqs = wallet.preparePending()
    req, = client.submitReqs(*reqs)
    return upgrade, req


def ensureUpgradeSent(looper, trustee, trusteeWallet, upgradeData):
    upgrade, req = sendUpgrade(trustee, trusteeWallet, upgradeData)
    waitForSufficientRepliesForRequests(looper, trustee, requests=[req],
                                      customTimeoutPerReq=10)

    def check():
        assert trusteeWallet.getPoolUpgrade(upgrade.key).seqNo

    looper.run(eventually(check, retryWait=1, timeout=5))
    return upgrade


def checkUpgradeScheduled(nodes, version):
    for node in nodes:
        assert len(node.upgrader.aqStash) > 0
        assert node.upgrader.scheduledUpgrade
        assert node.upgrader.scheduledUpgrade[0] == version


def checkNoUpgradeScheduled(nodes):
    for node in nodes:
        assert len(node.upgrader.aqStash) == 0
        assert node.upgrader.scheduledUpgrade is None


def codeVersion():
    return Upgrader.getVersion()


def bumpVersion(v):
    parts = v.split('.')
    return '.'.join(parts[:-1] + [str(int(parts[-1]) + 1)])


def bumpedVersion():
    v = codeVersion()
    return bumpVersion(v)
