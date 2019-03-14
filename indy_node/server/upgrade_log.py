from typing import Union
from datetime import datetime

from common.version import SourceVersion

from indy_common.version import src_version_cls
from indy_node.server.action_log import ActionLogData, ActionLogEvents, ActionLog


class UpgradeLogData(ActionLogData):
    _items = ActionLogData._items + ['version', 'upgrade_id', 'pkg_name']

    def __init__(
            self,
            when: Union[datetime, str],
            version: Union[SourceVersion, str],
            upgrade_id: str,
            pkg_name: str
    ):
        super().__init__(when)

        if isinstance(version, str):
            version = src_version_cls(pkg_name)(version)
        if not isinstance(version, SourceVersion):
            raise TypeError(
                "'version' should be 'SourceVersion' or 'str', got: {}"
                .format(type(version))
            )

        self.version = version
        self.upgrade_id = upgrade_id
        self.pkg_name = pkg_name


class UpgradeLog(ActionLog):

    Events = ActionLogEvents

    """
    Append-only event log of upgrade event
    """
    def __init__(self, file_path: str):
        super().__init__(
            file_path,
            data_class=UpgradeLogData,
            event_types=ActionLogEvents,
            delimiter='\t'
        )

    def append_scheduled(self, data: UpgradeLogData):
        super().append_scheduled(data)

    def append_started(self, data: UpgradeLogData):
        super().append_started(data)

    def append_succeeded(self, data: UpgradeLogData):
        super().append_succeeded(data)

    def append_failed(self, data: UpgradeLogData):
        super().append_failed(data)

    def append_cancelled(self, data: UpgradeLogData):
        super().append_cancelled(data)
