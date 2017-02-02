import csv
from datetime import datetime
from dateutil.parser import parse as parseDate
from os import path


class UpgradeLog:
    """
    Append-only event log of upgrade event
    """

    UPGRADE_SCHEDULED = "scheduled"
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
                    recordDate = parseDate(item[0])
                    event = item[1]
                    when = parseDate(item[2])
                    version = item[3]
                    parsed = (recordDate, event, when, version)
                    self.__items.append(parsed)

    @property
    def lastEvent(self):
        return self.__items[-1] if self.__items else None

    def appendScheduled(self, when, version) -> None:
        self.__append(UpgradeLog.UPGRADE_SCHEDULED, when, version)

    def appendSucceeded(self, when, version) -> None:
        self.__append(UpgradeLog.UPGRADE_SUCCEEDED, when, version)

    def appendFailed(self, when, version) -> None:
        self.__append(UpgradeLog.UPGRADE_FAILED, when, version)

    def appendCancelled(self, when, version) -> None:
        self.__append(UpgradeLog.UPGRADE_CANCELLED, when, version)

    def __append(self, type, when, version) -> None:
        """
        Appends event to log
        Be careful it opens file every time!
        """

        now = datetime.utcnow()
        event = (now, type, when, version)

        with open(self.__filePath, mode="a+", newline="") as file:
            writer = csv.writer(file, delimiter=self.__delimiter)
            writer.writerow(event)
        self.__items.append(event)

    def __iter__(self):
        return self

    def __next__(self):
        for item in self.__items:
            yield item
