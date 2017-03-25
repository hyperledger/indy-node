import os
from datetime import datetime

import dateutil.tz
import pytest

import sovrin_node
from stp_core.loop.eventually import eventually
from plenum.common.txn import TXN_TYPE
from plenum.common.types import OPERATION, f
from sovrin_common.txn import NODE_UPGRADE
from sovrin_node.server.upgrade_log import UpgradeLog
from sovrin_node.test.upgrade.helper import bumpedVersion

oldVersion = sovrin_node.__metadata__.__version_info__
oldVersionStr = sovrin_node.__metadata__.__version__

# Increasing the version of code
newVer = bumpedVersion()
sovrin_node.__metadata__.__version__ = newVer
sovrin_node.__metadata__.__version_info__ = tuple(int(v) for v in
                                                  newVer.split('.'))


from sovrin_node.test.conftest import tdirWithPoolTxns, poolTxnNodeNames

whitelist = ['unable to send message']
# TODO: Implement a client in node


@pytest.fixture(scope="module")
def tdirWithPoolTxns(tdirWithPoolTxns, poolTxnNodeNames, tconf):
    # For each node, adding a file with old version number which makes the node
    # think that an upgrade has been performed
    for nm in poolTxnNodeNames:
        path = os.path.join(tdirWithPoolTxns, tconf.nodeDataDir, nm)
        os.makedirs(path)
        # with open(os.path.join(path, tconf.lastRunVersionFile), 'w') as f:
        #     f.write(oldVersionStr)
        l = UpgradeLog(os.path.join(path, tconf.upgradeLogFile))
        when = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
        l.appendScheduled(when, sovrin_node.__metadata__.__version__)
    return tdirWithPoolTxns


@pytest.fixture(scope="module")
def upgradeSentToAllNodes(looper, nodeSet, nodeIds):
    def check():
        for node in nodeSet:
            assert len(node.configLedger) == len(nodeSet)
            ids = set()
            for txn in node.configLedger.getAllTxn().values():
                assert txn[TXN_TYPE] == NODE_UPGRADE
                ids.add(txn[f.IDENTIFIER.nm])
            ids.add(node.id)

            assert ids == set(nodeIds)

    looper.run(eventually(check, retryWait=1, timeout=5))


def testNodeDetectsUpgradeDone(looper, nodeSet):
    def check():
        for node in nodeSet:
            assert node.upgrader.lastExecutedUpgradeInfo[1] == newVer

    looper.run(eventually(check, retryWait=1, timeout=5))


def testSendNodeUpgradeToAllNodes(upgradeSentToAllNodes):
    pass
