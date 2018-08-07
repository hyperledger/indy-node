from indy_node.server.upgrade_log import UpgradeLog
from indy_node.test.upgrade.helper import count_action_log_entries


def test_pool_upgrade_force_scheduled_only_once(validUpgradeExpForceTrue, upgradeScheduledExpForceTrue, nodeSet):
    for node in nodeSet:
        assert count_action_log_entries(list(node.upgrader._actionLog),
                                        lambda entry: entry[5] == validUpgradeExpForceTrue['package']) == 1
        assert node.upgrader._actionLog.lastEvent[1] == UpgradeLog.SCHEDULED
