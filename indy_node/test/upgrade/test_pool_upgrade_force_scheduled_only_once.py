from indy_node.server.upgrade_log import UpgradeLog


def test_pool_upgrade_force_scheduled_only_once(upgradeScheduledExpForceTrue,
                                                nodeSet):
    for node in nodeSet:
        assert len(list(node.upgrader._upgradeLog)) == 1
        assert node.upgrader._upgradeLog.lastEvent[1] == \
               UpgradeLog.UPGRADE_SCHEDULED
