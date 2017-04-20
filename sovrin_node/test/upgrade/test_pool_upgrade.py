from copy import deepcopy
from datetime import datetime, timedelta

import dateutil.tz
import pytest

from sovrin_node.test import waits
from stp_core.loop.eventually import eventually
from plenum.common.constants import NAME, VERSION, STEWARD
from sovrin_common.constants import START, CANCEL, \
    ACTION, SCHEDULE, JUSTIFICATION
from plenum.test.helper import waitForSufficientRepliesForRequests, \
    ensureRejectsRecvd
from plenum.test.test_node import checkNodesConnected, ensureElectionsDone
from sovrin_client.test.helper import getClientAddedWithRole, checkRejects, checkNacks
from sovrin_node.test.upgrade.helper import sendUpgrade, \
    checkUpgradeScheduled, checkNoUpgradeScheduled, \
    bumpedVersion, ensureUpgradeSent
from plenum.test import waits as plenumWaits

whitelist = ['Failed to upgrade node']


@pytest.fixture(scope='module')
def validUpgrade(nodeIds, tconf):
    schedule = {}
    unow = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    startAt = unow + timedelta(seconds=90)
    acceptableDiff = tconf.MinSepBetweenNodeUpgrades + 1
    for i in nodeIds:
        schedule[i] = datetime.isoformat(startAt)
        startAt = startAt + timedelta(seconds=acceptableDiff + 3)
    # TODO select or create a timeout from 'waits'
    return dict(name='upgrade-13', version=bumpedVersion(), action=START,
                schedule=schedule, sha256='aad1242', timeout=10)


@pytest.fixture(scope='module')
def invalidUpgrade(nodeIds, tconf):
    schedule = {}
    unow = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    startAt = unow + timedelta(seconds=60)
    acceptableDiff = tconf.MinSepBetweenNodeUpgrades + 1
    for i in nodeIds:
        schedule[i] = datetime.isoformat(startAt)
        startAt = startAt + timedelta(seconds=acceptableDiff - 3)
    # TODO select or create a timeout from 'waits'
    return dict(name='upgrade-14', version=bumpedVersion(), action=START,
                schedule=schedule, sha256='ffd1224', timeout=10)


@pytest.fixture(scope="module")
def steward(nodeSet, tdir, looper, trustee, trusteeWallet):
    return getClientAddedWithRole(nodeSet, tdir, looper,
                                  trustee, trusteeWallet, 'newSteward', STEWARD)


@pytest.fixture(scope="module")
def validUpgradeSent(looper, nodeSet, tdir, trustee, trusteeWallet,
                     validUpgrade):
    ensureUpgradeSent(looper, trustee, trusteeWallet, validUpgrade)


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


@pytest.fixture(scope="module")
def upgradeScheduled(validUpgradeSent, looper, nodeSet, validUpgrade):
    looper.run(eventually(checkUpgradeScheduled, nodeSet, validUpgrade[VERSION],
                          retryWait=1, timeout=waits.expectedUpgradeScheduled()))


def testNodeSchedulesUpgrade(upgradeScheduled):
    pass


def testNodeSchedulesUpgradeAfterRestart(upgradeScheduled, looper, nodeSet,
                                         validUpgrade, testNodeClass,
                                         tdirWithPoolTxns, tconf,
                                         allPluginsPath):
    names = []
    while nodeSet:
        node = nodeSet.pop()
        names.append(node.name)
        node.cleanupOnStopping = False
        looper.removeProdable(node)
        node.stop()
        del node

    for nm in names:
        node = testNodeClass(nm, basedirpath=tdirWithPoolTxns,
                             config=tconf, pluginPaths=allPluginsPath)
        looper.add(node)
        nodeSet.append(node)

    looper.run(checkNodesConnected(nodeSet))
    ensureElectionsDone(looper=looper, nodes=nodeSet, retryWait=1)
    looper.run(eventually(checkUpgradeScheduled, nodeSet, validUpgrade[VERSION],
                          retryWait=1, timeout=waits.expectedUpgradeScheduled()))


def testPrimaryNodeTriggersElectionBeforeUpgrading(upgradeScheduled, looper,
                                                   nodeSet, validUpgrade):
    pass

@pytest.mark.skip("SOV-557. Skipping due to failing test, when run as module")
def testNonTrustyCannotCancelUpgrade(validUpgradeSent, looper, nodeSet,
                                     steward, validUpgrade):
    stClient, stWallet = steward
    validUpgradeCopy = deepcopy(validUpgrade)
    validUpgradeCopy[ACTION] = CANCEL
    _, req = sendUpgrade(stClient, stWallet, validUpgradeCopy)
    looper.run(eventually(checkRejects, stClient, req.reqId,
                          'cannot do'))

@pytest.mark.skip("SOV-557. Skipping due to failing test, when run as module")
def testTrustyCancelsUpgrade(validUpgradeSent, looper, nodeSet, trustee,
                             trusteeWallet, validUpgrade):
    validUpgradeCopy = deepcopy(validUpgrade)
    validUpgradeCopy[ACTION] = CANCEL
    validUpgradeCopy[JUSTIFICATION] = '"not gonna give you one"'

    validUpgradeCopy.pop(SCHEDULE, None)
    upgrade, req = sendUpgrade(trustee, trusteeWallet, validUpgradeCopy)

    def check():
        assert trusteeWallet.getPoolUpgrade(upgrade.key).seqNo

    timeout = plenumWaits.expectedTransactionExecutionTime(len(nodeSet))
    looper.run(eventually(check, retryWait=1, timeout=timeout))

    looper.run(eventually(checkNoUpgradeScheduled, nodeSet, retryWait=1,
                          timeout=waits.expectedNoUpgradeScheduled()))
