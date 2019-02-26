import csv
from abc import ABCMeta
from datetime import datetime
from os import path
from collections import namedtuple
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
        return parse_dt(when)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return str(self.__dict__)


class ActionLogRecord:
    def __init__(self, ev_type, ev_data: ActionLogData, record_ts=None):
        if record_ts and not isinstance(record_ts, datetime):
            raise TypeError(
                "'record_ts' should be 'datetime' or None, got: {}"
                .format(type(record_ts))
            )
        self.ts = record_ts if record_ts else datetime.utcnow()
        self.ev_type = ev_type
        self.ev_data = ev_data

    @property
    def packed(self):
        return [self.ts.isoformat(), self.ev_type.name] + list(self.ev_data.packed)

    @staticmethod
    def parse(row: Union[List, Tuple], data_class=ActionLogData):
        # TODO think about parse for 'data_class' or more generic serializer
        return ActionLogRecord(
            ActionLog.Events[row[1]], data_class(*data_class.parse(*row[2:])),
            record_ts=parse_dt(row[0]))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return str(self.__dict__)


# TODO
#   - tests
#   - rename lastEvent
class ActionLog(metaclass=ABCMeta):
    """
    Append-only event log of action event
    """

    Events = Enum('Events', 'scheduled started succeeded failed cancelled')

    def __init__(self, file_path, data_class=ActionLogData, delimiter="\t"):
        self.__delimiter = delimiter
        self.__file_path = file_path
        self.__items = []
        self._data_class = data_class
        self._load()

        for ev_type in self.Events:
            setattr(self, "append_{}".format(ev_type.name),
                    functools.partial(self._append, ev_type))

    @property
    def file_path(self):
        return self.__file_path

    @property
    def delimiter(self):
        return self.__delimiter

    @property
    def lastEvent(self):
        return self.__items[-1] if self.__items else None

    def _load(self):
        if path.exists(self.__file_path):
            with open(self.__file_path, mode="r", newline="") as file:
                reader = csv.reader(file, delimiter=self.__delimiter)
                for row in reader:
                    item = self._parse_item(row)
                    self.__items.append(item)

    def _append(self, ev_type, ev_data: ActionLogData) -> None:
        """
       Appends event to log
       Be careful it opens file every time!
       """
        record = ActionLogRecord(ev_type, ev_data)

        with open(self.__file_path, mode="a+", newline="") as file:
            writer = csv.writer(file, delimiter=self.__delimiter)
            writer.writerow(record.packed)
        self.__items.append(record)

    def _parse_item(self, row):
        return ActionLogRecord.parse(row, data_class=self._data_class)

    def __iter__(self):
        for item in self.__items:
            yield item

    def __len__(self):
        return len(self.__items)
