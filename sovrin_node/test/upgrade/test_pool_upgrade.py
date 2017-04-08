from copy import deepcopy
from datetime import datetime, timedelta

import dateutil.tz
import pytest

from stp_core.loop.eventually import eventually
from plenum.common.constants import NAME, VERSION, STEWARD
from sovrin_common.constants import START, CANCEL, \
    ACTION, SCHEDULE, JUSTIFICATION
from plenum.test.helper import checkSufficientRepliesForRequests, \
    ensureRejectsRecvd
from plenum.test.test_node import checkNodesConnected, ensureElectionsDone
from sovrin_client.test.helper import getClientAddedWithRole, checkNacks
from sovrin_node.test.upgrade.helper import sendUpgrade, \
    checkUpgradeScheduled, checkNoUpgradeScheduled, \
    bumpedVersion, ensureUpgradeSent


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
    with pytest.raises(AssertionError):
        checkSufficientRepliesForRequests(looper, trustee, [req, ],
                                          timeoutPerReq=10)
    looper.run(eventually(checkNacks, trustee, req.reqId,
                          'since time span between upgrades', retryWait=1,
                          timeout=10))


def testOnlyTrusteeCanSendPoolUpgrade(validUpgradeSent, looper, steward,
                                      validUpgrade, nodeSet):
    # A steward sending POOL_UPGRADE but txn fails
    stClient, stWallet = steward
    validUpgrade = deepcopy(validUpgrade)
    validUpgrade[NAME] = 'upgrade-20'
    validUpgrade[VERSION] = bumpedVersion()
    _, req = sendUpgrade(stClient, stWallet, validUpgrade)
    with pytest.raises(AssertionError):
        checkSufficientRepliesForRequests(looper, stClient, [req, ],
                                          timeoutPerReq=10)
    ensureRejectsRecvd(looper, nodeSet, stClient, 'cannot do')


@pytest.fixture(scope="module")
def upgradeScheduled(validUpgradeSent, looper, nodeSet, validUpgrade):
    looper.run(eventually(checkUpgradeScheduled, nodeSet, validUpgrade[VERSION],
                          retryWait=1, timeout=10))


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
    ensureElectionsDone(looper=looper, nodes=nodeSet, retryWait=1,
                        timeout=10)
    looper.run(eventually(checkUpgradeScheduled, nodeSet, validUpgrade[VERSION],
                          retryWait=1, timeout=10))


def testPrimaryNodeTriggersElectionBeforeUpgrading(upgradeScheduled, looper,
                                                   nodeSet, validUpgrade):
    pass


@pytest.mark.skip("SOV-557. Skipping due to failing test, when run as module")
def testNonTrustyCannotCancelUpgrade(validUpgradeSent, looper, nodeSet,
                                     steward, validUpgrade):
    stClient, stWallet = steward
    validUpgrade = deepcopy(validUpgrade)
    validUpgrade[ACTION] = CANCEL
    _, req = sendUpgrade(stClient, stWallet, validUpgrade)
    with pytest.raises(AssertionError):
        checkSufficientRepliesForRequests(looper, stClient, [req, ],
                                          timeoutPerReq=10)
    looper.run(eventually(checkNacks, stClient, req.reqId,
                          'cannot do'))


@pytest.mark.skip("SOV-558. Skipping due to failing test, when run as module")
def testTrustyCancelsUpgrade(validUpgradeSent, looper, nodeSet, trustee,
                             trusteeWallet, validUpgrade):
    validUpgrade = deepcopy(validUpgrade)
    validUpgrade[ACTION] = CANCEL
    validUpgrade[JUSTIFICATION] = '"not gonna give you one"'

    validUpgrade.pop(SCHEDULE, None)
    upgrade, req = sendUpgrade(trustee, trusteeWallet, validUpgrade)
    checkSufficientRepliesForRequests(looper, trustee, [req, ],
                                      timeoutPerReq=10)

    def check():
        assert trusteeWallet.getPoolUpgrade(upgrade.key).seqNo

    looper.run(eventually(check, retryWait=1, timeout=5))

    looper.run(eventually(checkNoUpgradeScheduled, nodeSet,
                          retryWait=1, timeout=10))
