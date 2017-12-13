import pytest

from indy_common.constants import FAIL
from indy_node.test.upgrade.helper import populate_log_with_upgrade_events, \
    bumpedVersion, check_node_sent_acknowledges_upgrade, check_node_do_not_sent_acknowledges_upgrade, \
    emulate_restart_pool_for_upgrade
from indy_node.server.upgrade_log import UpgradeLog

INVALID_VERSION = bumpedVersion()
whitelist = ['unable to send message',
             'failed upgrade',
             'This problem may have external reasons, check syslog for more information']


# TODO: Implement a client in node


@pytest.fixture(scope="module")
def tdirWithPoolTxns(tdirWithPoolTxns, poolTxnNodeNames, tdir, tconf):
    # For each node, adding a file with he current version number which makes the node
    # think that an upgrade has been performed
    populate_log_with_upgrade_events(
        poolTxnNodeNames, tdir, tconf, INVALID_VERSION)
    return tdirWithPoolTxns


def test_node_detected_upgrade_failed(nodeSet):
    '''
    Test that each node checks Upgrade Log on startup (after Upgrade restart), and writes FAIL to it
    because the current version differs from the one in Upgrade log.
    Upgrade log already created START event (see fixture above emulating real upgrade)
    '''
    for node in nodeSet:
        assert node.upgrader.scheduledUpgrade is None
        assert node.upgrader.lastUpgradeEventInfo[0] == UpgradeLog.UPGRADE_FAILED


def test_node_sent_upgrade_fail(looper, nodeSet, nodeIds):
    '''
    Test that each node sends NODE_UPGRADE Fail event (because it sees FAIL in Upgrade log)
    Upgrade log already created START event (see fixture above emulating real upgrade)
    '''
    check_node_sent_acknowledges_upgrade(looper, nodeSet, nodeIds,
                                         allowed_actions=[FAIL],
                                         ledger_size=len(nodeSet),
                                         expected_version=INVALID_VERSION)


def test_node_sent_upgrade_unsuccessful_once(looper, nodeSet, nodeIds):
    '''
    Test that each node sends NODE_UPGRADE Fail event only once,
    so that if we restart the node it's not sent again
    '''
    # emulate restart
    emulate_restart_pool_for_upgrade(nodeSet)

    # check that config ledger didn't changed (no new txns were sent)
    check_node_do_not_sent_acknowledges_upgrade(looper, nodeSet, nodeIds,
                                                allowed_actions=[FAIL],
                                                ledger_size=len(nodeSet),
                                                expected_version=INVALID_VERSION)
