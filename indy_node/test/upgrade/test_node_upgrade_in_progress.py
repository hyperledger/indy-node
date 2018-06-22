from indy_common.constants import IN_PROGRESS
from indy_node.test.upgrade.helper import check_node_sent_acknowledges_upgrade

whitelist = ['unable to send message']


def test_node_sent_upgrade_in_progress(looper, nodeSet, nodeIds, validUpgrade):
    '''
    Test that each node sends NODE_UPGRADE In Progress event
    (because it sees scheduledUpgrade in the Upgrader)
    '''
    version = validUpgrade['version']
    for node in nodeSet:
        node_id = node.poolManager.get_nym_by_name(node.name)
        node.upgrader.scheduledAction = (version,
                                 validUpgrade['schedule'][node_id],
                                 "upgrade_id")
        node.notify_upgrade_start()
    check_node_sent_acknowledges_upgrade(looper, nodeSet, nodeIds,
                                         allowed_actions=[IN_PROGRESS],
                                         ledger_size=len(nodeSet),
                                         expected_version=version)
