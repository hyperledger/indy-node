import pytest

import indy_node
from indy_common.constants import COMPLETE
from indy_node.test.upgrade.helper import populate_log_with_upgrade_events, \
    check_node_sent_acknowledges_upgrade, TestNodeNoProtocolVersion

whitelist = ['unable to send message']

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


@pytest.fixture(scope="module")
def testNodeClass(patchPluginManager):
    return TestNodeNoProtocolVersion


def test_node_sent_upgrade_successful_no_protocol_version(testNodeClass, looper, nodeSet, nodeIds):
    '''
    Test that each node sends NODE_UPGRADE Success event (because it sees SUCCESS in Upgrade log)
    Upgrade log already created START event (see fixture above emulating real upgrade)
    '''
    check_node_sent_acknowledges_upgrade(looper, nodeSet, nodeIds,
                                         allowed_actions=[COMPLETE],
                                         ledger_size=len(nodeSet),
                                         expected_version=version)
