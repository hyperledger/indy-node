import os
from datetime import datetime
import functools

import dateutil.tz
import pytest

import sovrin_node
from stp_core.loop.eventually import eventually
from plenum.common.constants import TXN_TYPE
from sovrin_common.constants import NODE_UPGRADE

from plenum.common.types import OPERATION, f
from sovrin_node.server.upgrade_log import UpgradeLog
from sovrin_node.test.upgrade.helper import bumpedVersion
from plenum.test import waits as plenumWaits
oldVersion = sovrin_node.__metadata__.__version_info__
oldVersionStr = sovrin_node.__metadata__.__version__

# Increasing the version of code
newVer = bumpedVersion()
sovrin_node.__metadata__.__version__ = newVer
sovrin_node.__metadata__.__version_info__ = tuple(int(v) for v in
                                                  newVer.split('.'))


whitelist = ['unable to send message']
# TODO: Implement a client in node


@pytest.fixture(scope="module")
def tdirWithPoolTxns(tdirWithPoolTxns, poolTxnNodeNames, tconf):
    # For each node, adding a file with old version number which makes the node
    # think that an upgrade has been performed
    for nm in poolTxnNodeNames:
        path = os.path.join(tdirWithPoolTxns, tconf.nodeDataDir, nm)
        os.makedirs(path)
        log = UpgradeLog(os.path.join(path, tconf.upgradeLogFile))
        when = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
        log.appendScheduled(when, sovrin_node.__metadata__.__version__)
        log.appendStarted(when, sovrin_node.__metadata__.__version__)
    return tdirWithPoolTxns


@pytest.fixture(scope="module")
def upgradeSentToAllNodes(looper, nodeSet, nodeIds):
    def check(ledger_size):
        for node in nodeSet:
            assert len(node.configLedger) == ledger_size
            ids = set()
            for _, txn in node.configLedger.getAllTxn():
                assert txn[TXN_TYPE] == NODE_UPGRADE
                ids.add(txn[f.IDENTIFIER.nm])
            ids.add(node.id)

            assert ids == set(nodeIds)

    for node in nodeSet:
        node.upgrader.scheduledUpgrade = (sovrin_node.__metadata__.__version__, 0)
        node.notify_upgrade_start()

    timeout = plenumWaits.expectedTransactionExecutionTime(len(nodeSet))
    looper.run(eventually(functools.partial(check, len(nodeSet)), retryWait=1, timeout=timeout))

    for node in nodeSet:
        node.acknowledge_upgrade()

    looper.run(eventually(functools.partial(check, 2 * len(nodeSet)), retryWait=1, timeout=timeout))


def testNodeDetectsUpgradeDone(looper, nodeSet):
    def check():
        for node in nodeSet:
            assert node.upgrader.lastUpgradeEventInfo[2] == newVer

    timeout = plenumWaits.expectedTransactionExecutionTime(len(nodeSet))
    looper.run(eventually(check, retryWait=1, timeout=timeout))


def testSendNodeUpgradeToAllNodes(upgradeSentToAllNodes):
    pass
