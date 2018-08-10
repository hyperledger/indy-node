import csv
from datetime import datetime
from os import path

from dateutil.parser import parse as parse_date

from indy_node.server.action_log import ActionLog


class UpgradeLog(ActionLog):
    """
    Append-only event log of upgrade event
    """

    def __init__(self, filePath, delimiter="\t"):
        super().__init__(filePath, delimiter)

    def appendScheduled(self, when, version, upgrade_id, pkg_name) -> None:
        self._append(UpgradeLog.SCHEDULED, when, version, upgrade_id, pkg_name)

    def appendStarted(self, when, version, upgrade_id, pkg_name) -> None:
        self._append(UpgradeLog.STARTED, when, version, upgrade_id, pkg_name)

    def appendSucceeded(self, when, version, upgrade_id, pkg_name) -> None:
        self._append(UpgradeLog.SUCCEEDED, when, version, upgrade_id, pkg_name)

    def appendFailed(self, when, version, upgrade_id, pkg_name) -> None:
        self._append(UpgradeLog.FAILED, when, version, upgrade_id, pkg_name)

    def appendCancelled(self, when, version, upgrade_id, pkg_name) -> None:
        self._append(UpgradeLog.CANCELLED, when, version, upgrade_id, pkg_name)

    def _parse_item(self, row):
        record_date, event, when = super()._parse_item(row)
        version = row[3]
        upgrade_id = None
        if len(row) > 4:
            upgrade_id = row[4]
        pkt_name = None
        if len(row) > 5:
            pkt_name = row[5]
        return record_date, event, when, version, upgrade_id, pkt_name
