import pytest

import indy_node
from indy_node.server.upgrade_log import UpgradeLog
from indy_common.constants import COMPLETE
from indy_node.test.upgrade.helper import populate_log_with_upgrade_events, \
    check_node_sent_acknowledges_upgrade, check_node_do_not_sent_acknowledges_upgrade, \
    emulate_restart_pool_for_upgrade, emulate_view_change_pool_for_upgrade

whitelist = ['unable to send message']
# TODO: Implement a client in node

version = indy_node.__metadata__.__version__


@pytest.fixture(scope="module")
def tdirWithPoolTxns(tdirWithPoolTxns, poolTxnNodeNames, tdir, tconf):
    # For each node, adding a file with he current version number which makes the node
    # think that an upgrade has been performed
    populate_log_with_upgrade_events(
        poolTxnNodeNames,
        tdir,
        tconf,
        version)
    return tdirWithPoolTxns


def test_node_detected_upgrade_done(nodeSet):
    '''
    Test that each node checks Upgrade Log on startup (after Upgrade restart), and writes SUCCESS to it
    because the current version equals to the one in Upgrade log.
    Upgrade log already created START event (see fixture above emulating real upgrade)
    '''
    for node in nodeSet:
        assert node.upgrader.scheduledAction is None
        assert node.upgrader.lastActionEventInfo[0] == UpgradeLog.SUCCEEDED


def test_node_sent_upgrade_successful(looper, nodeSet, nodeIds):
    '''
    Test that each node sends NODE_UPGRADE Success event (because it sees SUCCESS in Upgrade log)
    Upgrade log already created START event (see fixture above emulating real upgrade)
    '''
    check_node_sent_acknowledges_upgrade(looper, nodeSet, nodeIds,
                                         allowed_actions=[COMPLETE],
                                         ledger_size=len(nodeSet),
                                         expected_version=version)


def test_node_sent_upgrade_successful_once_view_change(looper, nodeSet, nodeIds):
    '''
    Test that each node sends NODE_UPGRADE Success event only once after each view change
    '''
    # emulate view changes 1-4
    emulate_view_change_pool_for_upgrade(nodeSet)
    emulate_view_change_pool_for_upgrade(nodeSet)
    emulate_view_change_pool_for_upgrade(nodeSet)
    emulate_view_change_pool_for_upgrade(nodeSet)

    # check that config ledger didn't changed (no new txns were sent)
    check_node_do_not_sent_acknowledges_upgrade(looper, nodeSet, nodeIds,
                                                allowed_actions=[COMPLETE],
                                                ledger_size=len(nodeSet),
                                                expected_version=version)


def test_node_sent_upgrade_successful_once_restart(looper, nodeSet, nodeIds):
    '''
    Test that each node sends NODE_UPGRADE Success event only once after restart,
    so that if we restart the node it's not sent again
    '''
    # emulate restart
    emulate_restart_pool_for_upgrade(nodeSet)

    # check that config ledger didn't changed (no new txns were sent)
    check_node_do_not_sent_acknowledges_upgrade(looper, nodeSet, nodeIds,
                                                allowed_actions=[COMPLETE],
                                                ledger_size=len(nodeSet),
                                                expected_version=version)