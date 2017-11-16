import pytest

from indy_common.constants import IN_PROGRESS, FAIL
from indy_node.test.upgrade.helper import populate_log_with_upgrade_events, check_node_set_acknowledges_upgrade, \
    bumpedVersion
from indy_node.server.upgrade_log import UpgradeLog


INVALID_VERSION = bumpedVersion()
whitelist = ['unable to send message',
             'failed upgrade',
             'This problem may have external reasons, check syslog for more information']

# TODO: Implement a client in node


@pytest.fixture(scope="module")
def tdirWithPoolTxns(tdirWithPoolTxns, poolTxnNodeNames, tconf):
    # For each node, adding a file with he current version number which makes the node
    # think that an upgrade has been performed
    populate_log_with_upgrade_events(
        tdirWithPoolTxns, poolTxnNodeNames, tconf, INVALID_VERSION)
    return tdirWithPoolTxns


def test_node_handles_unsuccessful_upgrade(looper, nodeSet, nodeIds):
    check_node_set_acknowledges_upgrade(looper, nodeSet, nodeIds, [
                                        IN_PROGRESS, FAIL], INVALID_VERSION)

    for node in nodeSet:
        assert node.upgrader.scheduledUpgrade is None
        assert node.upgrader.lastUpgradeEventInfo[0] == UpgradeLog.UPGRADE_FAILED
