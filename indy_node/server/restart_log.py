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
                    restart_id = None  # default parameter required for backward compatibility
                    if len(item) > 3:
                        restart_id = item[3]
                    parsed = (record_date, event, when, restart_id)
                    self.__items.append(parsed)

    @property
    def lastEvent(self):
        return self.__items[-1] if self.__items else None

    def appendScheduled(self, when, restart_id) -> None:
        self.__append(RestartLog.RESTART_SCHEDULED, when, restart_id)

    def appendStarted(self, when, restart_id) -> None:
        self.__append(RestartLog.RESTART_STARTED, when, restart_id)

    def appendSucceeded(self, when, restart_id) -> None:
        self.__append(RestartLog.RESTART_SUCCEEDED, when, restart_id)

    def appendFailed(self, when, restart_id) -> None:
        self.__append(RestartLog.RESTART_FAILED, when, restart_id)

    def appendCancelled(self, when, restart_id) -> None:
        self.__append(RestartLog.RESTART_CANCELLED, when, restart_id)

    def __append(self, type, when, restart_id) -> None:
        """
        Appends event to log
        Be careful it opens file every time!
        """

        now = datetime.utcnow()
        event = (now, type, when, restart_id)

        with open(self.__filePath, mode="a+", newline="") as file:
            writer = csv.writer(file, delimiter=self.__delimiter)
            writer.writerow(event)
        self.__items.append(event)

    def __iter__(self):
        for item in self.__items:
            yield item

    def __len__(self):
        return len(self.__items)
