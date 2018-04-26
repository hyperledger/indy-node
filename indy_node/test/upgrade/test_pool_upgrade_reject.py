from copy import deepcopy

from plenum.common.constants import NAME, VERSION
from plenum.test import waits as plenumWaits
from indy_client.test.helper import checkRejects, checkNacks
from indy_common.constants import CANCEL, \
    ACTION
from indy_node.test.upgrade.helper import sendUpgrade, ensureUpgradeSent, \
    bumpedVersion
from stp_core.loop.eventually import eventually

whitelist = ['Failed to upgrade node']


def testNodeRejectsPoolUpgrade(looper, nodeSet, tdir, trustee,
                               trusteeWallet, invalidUpgrade):
    _, req = sendUpgrade(trustee, trusteeWallet, invalidUpgrade)
    timeout = plenumWaits.expectedReqNAckQuorumTime()
    looper.run(eventually(checkNacks, trustee, req.reqId,
                          'since time span between upgrades', retryWait=1,
                          timeout=timeout))


def testOnlyTrusteeCanSendPoolUpgrade(looper, steward, validUpgrade):
    # A steward sending POOL_UPGRADE but txn fails
    stClient, stWallet = steward
    validUpgrade = deepcopy(validUpgrade)
    validUpgrade[NAME] = 'upgrade-20'
    validUpgrade[VERSION] = bumpedVersion()
    _, req = sendUpgrade(stClient, stWallet, validUpgrade)
    timeout = plenumWaits.expectedReqNAckQuorumTime()
    looper.run(eventually(checkRejects, stClient, req.reqId,
                          'cannot do', retryWait=1, timeout=timeout))


def testNonTrustyCannotCancelUpgrade(looper, validUpgradeSent,
                                     steward, validUpgrade):
    stClient, stWallet = steward
    validUpgradeCopy = deepcopy(validUpgrade)
    validUpgradeCopy[ACTION] = CANCEL
    _, req = sendUpgrade(stClient, stWallet, validUpgradeCopy)
    looper.run(eventually(checkRejects, stClient, req.reqId,
                          'cannot do'))


def test_accept_then_reject_upgrade(
        looper, trustee, trusteeWallet, validUpgradeSent, validUpgrade):
    upgrade_name = validUpgrade[NAME]
    error_msg = "InvalidClientRequest(\"Upgrade '{}' is already scheduled\"".\
        format(upgrade_name)

    validUpgrade2 = deepcopy(validUpgrade)

    _, req = sendUpgrade(trustee, trusteeWallet, validUpgrade2)
    timeout = plenumWaits.expectedReqNAckQuorumTime()

    looper.run(eventually(checkRejects, trustee, req.reqId,
                          error_msg, retryWait=1, timeout=timeout))


def testOnlyTrusteeCanSendPoolUpgradeForceTrue(
        looper, steward, validUpgradeExpForceTrue):
    stClient, stWallet = steward
    _, req = sendUpgrade(stClient, stWallet, validUpgradeExpForceTrue)
    timeout = plenumWaits.expectedReqNAckQuorumTime()
    looper.run(eventually(checkNacks, stClient, req.reqId,
                          'cannot do', retryWait=1, timeout=timeout))
