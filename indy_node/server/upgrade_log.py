from datetime import datetime

from indy_node.server.action_log import ActionLogData, ActionLog


# TODO tests
class UpgradeLogData(ActionLogData):
    def __init__(self, when: datetime,
                 version: str, upgrade_id: str, pkg_name: str):
        super().__new__(when)
        self.version = version
        self.upgrade_id = upgrade_id
        self.pkg_name = pkg_name

    @property
    def packed(self):
        return (super().packed +
                [self.version, self.upgrade_id, self.pkg_name])

    @staticmethod
    def parse(when, version, upgrade_id, pkg_name):
        return ActionLogData.parse(when) + [version, upgrade_id, pkg_name]


class UpgradeLog(ActionLog):
    """
    Append-only event log of upgrade event
    """
    def __init__(self, *args, data_class=UpgradeLogData, **kwargs):
        super().__init__(*args, data_class=data_class, **kwargs)
