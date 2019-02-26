import csv
from abc import ABCMeta
from datetime import datetime
from os import path
from typing import Union, Tuple, List
import functools
from enum import Enum

from dateutil.parser import parse as parse_dt


# TODO tests
class ActionLogData:
    def __init__(self, when: datetime):
        if not isinstance(when, datetime):
            raise TypeError(
                "'when' should be 'datetime' or 'str', got: {}"
                .format(type(when))
            )
        self.when = when

    @property
    def packed(self):
        return [self.when.isoformat()]

    @staticmethod
    def parse(when):
        return [parse_dt(when)]

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return str(self.__dict__)


class ActionLogEvent:
    def __init__(self, ev_type, data: ActionLogData, ts=None):
        if ts and not isinstance(ts, datetime):
            raise TypeError(
                "'ts' should be 'datetime' or None, got: {}"
                .format(type(ts))
            )
        self.ts = ts if ts else datetime.utcnow()
        self.ev_type = ev_type
        self.data = data

    @property
    def packed(self):
        return [self.ts.isoformat(), self.ev_type.name] + list(self.data.packed)

    @staticmethod
    def parse(row: Union[List, Tuple], data_class=ActionLogData):
        # TODO think about parse for 'data_class' or more generic serializer
        return ActionLogEvent(
            ActionLog.Events[row[1]], data_class(*data_class.parse(*row[2:])),
            ts=parse_dt(row[0]))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return str(self.__dict__)


class ActionLog(metaclass=ABCMeta):
    """
    Append-only event log of action event
    """

    Events = Enum('Events', 'scheduled started succeeded failed cancelled')

    def __init__(self, file_path, data_class=ActionLogData, delimiter="\t"):
        self._delimiter = delimiter
        self._file_path = file_path
        self._items = []
        self._data_class = data_class
        self._load()

        for ev_type in self.Events:
            setattr(self, "append_{}".format(ev_type.name),
                    functools.partial(self._append, ev_type))

    @property
    def file_path(self):
        return self._file_path

    @property
    def delimiter(self):
        return self._delimiter

    @property
    def last_event(self):
        return self._items[-1] if self._items else None

    def _load(self):
        if path.exists(self._file_path):
            with open(self._file_path, mode="r", newline="") as file:
                reader = csv.reader(file, delimiter=self._delimiter)
                for row in reader:
                    item = self._parse_item(row)
                    self._items.append(item)

    def _append(self, ev_type, *data: ActionLogData) -> None:
        """
        Appends event to log
        Be careful it opens file every time!
        """

        record = ActionLogEvent(
            ev_type,
            (data[0] if len(data) == 1 and
             type(data[0]) is self._data_class else
             self._data_class(*data))
        )

        with open(self._file_path, mode="a+", newline="") as file:
            writer = csv.writer(file, delimiter=self._delimiter)
            writer.writerow(record.packed)
        self._items.append(record)

    def _parse_item(self, row):
        return ActionLogEvent.parse(row, data_class=self._data_class)

    def __iter__(self):
        for item in self._items:
            yield item

    def __len__(self):
        return len(self._items)
