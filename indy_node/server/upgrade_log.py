import csv
from datetime import datetime
from os import path

from dateutil.parser import parse as parse_date


class UpgradeLog:
    """
    Append-only event log of upgrade event
    """

    UPGRADE_SCHEDULED = "scheduled"
    UPGRADE_STARTED = "started"
    UPGRADE_SUCCEEDED = "succeeded"
    UPGRADE_FAILED = "failed"
    UPGRADE_CANCELLED = "cancelled"

    def __init__(self, filePath, delimiter="\t"):
        self.__delimiter = delimiter
        self.__filePath = filePath
        self.__items = []
        self.__load()

    def __load(self):

        if path.exists(self.__filePath):
            with open(self.__filePath, mode="r", newline="") as file:
                reader = csv.reader(file, delimiter=self.__delimiter)
                for item in reader:
                    record_date = parse_date(item[0])
                    event = item[1]
                    when = parse_date(item[2])
                    version = item[3]
                    upgrade_id = None  # default parameter required for backward compatibility
                    if len(item) > 4:
                        upgrade_id = item[4]
                    parsed = (record_date, event, when, version, upgrade_id)
                    self.__items.append(parsed)

    @property
    def lastEvent(self):
        return self.__items[-1] if self.__items else None

    def appendScheduled(self, when, version, upgrade_id) -> None:
        self.__append(UpgradeLog.UPGRADE_SCHEDULED, when, version, upgrade_id)

    def appendStarted(self, when, version, upgrade_id) -> None:
        self.__append(UpgradeLog.UPGRADE_STARTED, when, version, upgrade_id)

    def appendSucceeded(self, when, version, upgrade_id) -> None:
        self.__append(UpgradeLog.UPGRADE_SUCCEEDED, when, version, upgrade_id)

    def appendFailed(self, when, version, upgrade_id) -> None:
        self.__append(UpgradeLog.UPGRADE_FAILED, when, version, upgrade_id)

    def appendCancelled(self, when, version, upgrade_id) -> None:
        self.__append(UpgradeLog.UPGRADE_CANCELLED, when, version, upgrade_id)

    def __append(self, type, when, version, upgrade_id) -> None:
        """
        Appends event to log
        Be careful it opens file every time!
        """

        now = datetime.utcnow()
        event = (now, type, when, version, upgrade_id)

        with open(self.__filePath, mode="a+", newline="") as file:
            writer = csv.writer(file, delimiter=self.__delimiter)
            writer.writerow(event)
        self.__items.append(event)

    def __iter__(self):
        for item in self.__items:
            yield item

    def __len__(self):
        return len(self.__items)
