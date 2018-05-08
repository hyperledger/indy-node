import csv
from abc import ABCMeta
from datetime import datetime
from os import path

from dateutil.parser import parse as parse_date


class ActionLog(metaclass=ABCMeta):
    """
    Append-only event log of action event
    """

    SCHEDULED = "scheduled"
    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

    def __init__(self, filePath, delimiter="\t"):
        self.__delimiter = delimiter
        self.__filePath = filePath
        self.__items = []
        self._load()

    @property
    def lastEvent(self):
        return self.__items[-1] if self.__items else None

    def _load(self):
        if path.exists(self.__filePath):
            with open(self.__filePath, mode="r", newline="") as file:
                reader = csv.reader(file, delimiter=self.__delimiter)
                for row in reader:
                    item = self._parse_item(row)
                    self.__items.append(item)

    def _append(self, type, when, *args) -> None:
        """
       Appends event to log
       Be careful it opens file every time!
       """
        now = datetime.utcnow()
        event = (now, type, when, *args)

        with open(self.__filePath, mode="a+", newline="") as file:
            writer = csv.writer(file, delimiter=self.__delimiter)
            writer.writerow(event)
        self.__items.append(event)

    def _parse_item(self, row):
        record_date = parse_date(row[0])
        event = row[1]
        when = parse_date(row[2])
        return record_date, event, when

    def __iter__(self):
        for item in self.__items:
            yield item

    def __len__(self):
        return len(self.__items)
