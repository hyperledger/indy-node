from indy_node.server.upgrade_log import UpgradeLog
from indy_node.test.upgrade.helper import count_action_log_package


def test_pool_upgrade_force_scheduled_only_once(validUpgradeExpForceTrue, upgradeScheduledExpForceTrue, nodeSet):
    for node in nodeSet:
        assert count_action_log_package(list(node.upgrader._actionLog), validUpgradeExpForceTrue['package']) == 1
        assert node.upgrader._actionLog.last_event.ev_type == UpgradeLog.Events.scheduled
