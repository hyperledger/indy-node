import dateutil

from indy_node.server.upgrade_log import UpgradeLog
from indy_node.test.upgrade.helper import emulate_view_change_pool_for_upgrade

whitelist = ['unable to send message']


# TODO: Implement a client in node


def test_scheduled_once_after_view_change(nodeSet, validUpgrade, upgradeScheduled):
    '''
    Test that each node schedules update only once after each view change
    '''
    # emulate view changes 1-4
    emulate_view_change_pool_for_upgrade(nodeSet)
    emulate_view_change_pool_for_upgrade(nodeSet)
    emulate_view_change_pool_for_upgrade(nodeSet)
    emulate_view_change_pool_for_upgrade(nodeSet)

    # check that there are no cancel events in Upgrade log
    version = validUpgrade['version']
    upgrade_id = nodeSet[0].upgrader.scheduledUpgrade[2]
    for node in nodeSet:
        node_id = node.poolManager.get_nym_by_name(node.name)
        when = dateutil.parser.parse(validUpgrade['schedule'][node_id])
        assert node.upgrader.scheduledUpgrade == (version, when, upgrade_id)
        assert len(node.upgrader._upgradeLog) == 1
        assert node.upgrader.lastUpgradeEventInfo == (UpgradeLog.UPGRADE_SCHEDULED, when, version, upgrade_id)
