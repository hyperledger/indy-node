from datetime import datetime, timedelta

import dateutil.tz
import pytest
from plenum.common.constants import VERSION, STEWARD
from plenum.common.util import randomString
from sovrin_client.test.helper import getClientAddedWithRole

from sovrin_common.constants import START, FORCE
from sovrin_node.test import waits
from sovrin_node.test.upgrade.helper import bumpedVersion, ensureUpgradeSent, \
    checkUpgradeScheduled, bumpVersion, get_valid_code_hash
from stp_core.loop.eventually import eventually


@pytest.fixture(scope='module')
def nodeIds(nodeSet):
    return nodeSet[0].poolManager.nodeIds


@pytest.fixture(scope='module')
def validUpgrade(nodeIds, tconf):
    schedule = {}
    unow = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    startAt = unow + timedelta(seconds=30)
    acceptableDiff = tconf.MinSepBetweenNodeUpgrades + 1
    for i in nodeIds:
        schedule[i] = datetime.isoformat(startAt)
        startAt = startAt + timedelta(seconds=acceptableDiff + 3)
    return dict(name='upgrade-13', version=bumpedVersion(), action=START,
                schedule=schedule,
                # sha256=get_valid_code_hash(),
                sha256='db34a72a90d026dae49c3b3f0436c8d3963476c77468ad955845a1ccf7b03f55',
                timeout=1)


@pytest.fixture(scope='module')
def validUpgradeExpForceFalse(validUpgrade):
    nup = validUpgrade.copy()
    nup.update({FORCE: False})
    nup.update({VERSION: bumpVersion(validUpgrade[VERSION])})
    return nup


@pytest.fixture(scope='module')
def validUpgradeExpForceTrue(validUpgradeExpForceFalse):
    nup = validUpgradeExpForceFalse.copy()
    nup.update({FORCE: True})
    nup.update({VERSION: bumpVersion(validUpgradeExpForceFalse[VERSION])})
    return nup


@pytest.fixture(scope="module")
def validUpgradeSent(looper, nodeSet, tdir, trustee, trusteeWallet,
                     validUpgrade):
    ensureUpgradeSent(looper, trustee, trusteeWallet, validUpgrade)


@pytest.fixture(scope="module")
def validUpgradeSentExpForceFalse(looper, nodeSet, tdir, trustee, trusteeWallet,
                                  validUpgradeExpForceFalse):
    ensureUpgradeSent(looper, trustee, trusteeWallet, validUpgradeExpForceFalse)


@pytest.fixture(scope="module")
def validUpgradeSentExpForceTrue(looper, nodeSet, tdir, trustee, trusteeWallet,
                                 validUpgradeExpForceTrue):
    ensureUpgradeSent(looper, trustee, trusteeWallet, validUpgradeExpForceTrue)


@pytest.fixture(scope="module")
def upgradeScheduled(validUpgradeSent, looper, nodeSet, validUpgrade):
    looper.run(eventually(checkUpgradeScheduled, nodeSet, validUpgrade[VERSION],
                          retryWait=1, timeout=waits.expectedUpgradeScheduled()))


@pytest.fixture(scope="module")
def upgradeScheduledExpForceFalse(validUpgradeSentExpForceFalse, looper,
                                  nodeSet, validUpgradeExpForceFalse):
    looper.run(eventually(checkUpgradeScheduled, nodeSet,
                          validUpgradeExpForceFalse[VERSION], retryWait=1,
                          timeout=waits.expectedUpgradeScheduled()))


@pytest.fixture(scope="module")
def upgradeScheduledExpForceTrue(validUpgradeSentExpForceTrue, looper, nodeSet,
                                 validUpgradeExpForceTrue):
    looper.run(eventually(checkUpgradeScheduled, nodeSet,
                          validUpgradeExpForceTrue[VERSION], retryWait=1,
                          timeout=waits.expectedUpgradeScheduled()))


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
                schedule=schedule,
                # sha256=get_valid_code_hash(),
                sha256='46c715a90b1067142d548cb1f1405b0486b32b1a27d418ef3a52bd976e9fae50',
                timeout=10)


@pytest.fixture(scope="module")
def steward(nodeSet, tdir, looper, trustee, trusteeWallet):
    return getClientAddedWithRole(nodeSet, tdir, looper,
                                  trustee, trusteeWallet, 'newSteward', STEWARD)