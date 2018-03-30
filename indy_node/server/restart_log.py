import csv
from datetime import datetime
from os import path

from dateutil.parser import parse as parse_date


class RestartLog:
    """
    Append-only event log of restart event
    """

    RESTART_SCHEDULED = "scheduled"
    RESTART_STARTED = "started"
    RESTART_SUCCEEDED = "succeeded"
    RESTART_FAILED = "failed"
    RESTART_CANCELLED = "cancelled"

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
                    parsed = (record_date, event, when)
                    self.__items.append(parsed)

    @property
    def lastEvent(self):
        return self.__items[-1] if self.__items else None

    def appendScheduled(self, when) -> None:
        self.__append(RestartLog.RESTART_SCHEDULED, when)

    def appendStarted(self, when) -> None:
        self.__append(RestartLog.RESTART_STARTED, when)

    def appendSucceeded(self, when) -> None:
        self.__append(RestartLog.RESTART_SUCCEEDED, when)

    def appendFailed(self, when) -> None:
        self.__append(RestartLog.RESTART_FAILED, when)

    def appendCancelled(self, when) -> None:
        self.__append(RestartLog.RESTART_CANCELLED, when)

    def __append(self, type, when) -> None:
        """
        Appends event to log
        Be careful it opens file every time!
        """

        now = datetime.utcnow()
        event = (now, type, when)

        with open(self.__filePath, mode="a+", newline="") as file:
            writer = csv.writer(file, delimiter=self.__delimiter)
            writer.writerow(event)
        self.__items.append(event)

    def __iter__(self):
        for item in self.__items:
            yield item

    def __len__(self):
        return len(self.__items)
