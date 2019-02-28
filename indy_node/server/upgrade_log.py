from datetime import datetime

from indy_node.server.action_log import ActionLogData, ActionLog


# TODO tests
class UpgradeLogData(ActionLogData):
    _items = ActionLogData._items + ['version', 'upgrade_id', 'pkg_name']

    def __init__(self, when: datetime,
                 version: str, upgrade_id: str, pkg_name: str):
        super().__init__(when)
        self.version = version
        self.upgrade_id = upgrade_id
        self.pkg_name = pkg_name


class UpgradeLog(ActionLog):
    """
    Append-only event log of upgrade event
    """
    pass
