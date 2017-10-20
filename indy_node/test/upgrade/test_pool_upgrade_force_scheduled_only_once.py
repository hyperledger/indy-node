from indy_node.server.upgrade_log import UpgradeLog


def testPoolUpgradeForceScheduledOnlyOnce(upgradeScheduledExpForceTrue,
                                          nodeSet):
    for node in nodeSet:
        assert len(list(node.upgrader._upgradeLog)) == 1
        assert node.upgrader._upgradeLog.lastEvent[1] == \
               UpgradeLog.UPGRADE_SCHEDULED
