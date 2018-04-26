import csv
from datetime import datetime
from os import path

from dateutil.parser import parse as parse_date

from indy_node.server.action_log import ActionLog


class RestartLog(ActionLog):
    """
    Append-only event log of restart event
    """

    def __init__(self, filePath, delimiter="\t"):
        super().__init__(filePath, delimiter)

    def appendScheduled(self, when) -> None:
        self._append(RestartLog.SCHEDULED, when)

    def appendStarted(self, when) -> None:
        self._append(RestartLog.STARTED, when)

    def appendSucceeded(self, when) -> None:
        self._append(RestartLog.SUCCEEDED, when)

    def appendFailed(self, when) -> None:
        self._append(RestartLog.FAILED, when)

    def appendCancelled(self, when) -> None:
        self._append(RestartLog.CANCELLED, when)
