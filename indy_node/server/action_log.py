import csv
import io
import os
import datetime
import functools
from typing import Type, Union, Tuple
from enum import Enum, unique
from dateutil.parser import parse as parse_dt

# TODO
#  - move csv serializer to separate module


class CsvSerializer:
    _items = []

    def __iter__(self):
        for item in self._items:
            yield getattr(self, item)

    def pack(self, delimiter: str = '\t'):
        with io.StringIO() as fs:
            csv.writer(fs, delimiter=delimiter).writerow(self)
            return fs.getvalue()

    @classmethod
    def unpack(cls, row: str, *args, delimiter: str = '\t', **kwargs):
        reader = csv.reader([row], delimiter=delimiter)
        return cls(*next(reader), *args, **kwargs)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return str(self.__dict__)


class ActionLogData(CsvSerializer):
    _items = ['when']

    def __init__(self, when: Union[datetime.datetime, str]):
        if isinstance(when, str):
            when = parse_dt(when)
        if not isinstance(when, datetime.datetime):
            raise TypeError(
                "'when' should be 'datetime' or 'str', got: {}"
                .format(type(when))
            )
        self.when = when


@unique
class ActionLogEvents(Enum):
    scheduled = 1
    started = 2
    succeeded = 3
    failed = 4
    cancelled = 5

    def __str__(self):
        return self.name


# Note. datetime class is referred not directly (through datetime module)
# since it makes possible to mock it in tests using subclasses
class ActionLogEvent(CsvSerializer):
    def __init__(
            self,
            ts: Union[datetime.datetime, str],
            ev_type: Enum,
            data: Type[Union[CsvSerializer, str]],
            *args: Tuple[str],
            data_class: Type[Union[CsvSerializer, None]] = None,
            types: Type[Enum] = ActionLogEvents
    ):
        if ts:
            if isinstance(ts, str):
                ts = parse_dt(ts)
            if not isinstance(ts, datetime.datetime):
                raise TypeError(
                    "'ts' should be 'datetime' or None, got: {}"
                    .format(type(ts))
                )

        if isinstance(ev_type, str):
            try:
                ev_type = types[ev_type]
            except KeyError:
                raise ValueError("Unknown event {}"
                                 .format(ev_type))

        if not isinstance(ev_type, Enum):
            raise TypeError(
                "'ev_type' should be 'Enum', got: {}"
                .format(type(ts))
            )

        if ev_type not in types:
            raise ValueError("Unknown event {}".format(ev_type))

        data = data_class(data, *args) if data_class else data
        if not isinstance(data, CsvSerializer):
            raise TypeError(
                "'data' should be 'CsvSerializer', got: {}"
                .format(type(data))
            )

        self.ts = ts if ts else datetime.datetime.utcnow()
        self.ev_type = ev_type
        self.data = data

        self._data_items_prefix = '_data_'
        self._items = (
            ['ts', 'ev_type'] +
            [(self._data_items_prefix + i) for i in self.data._items]
        )
        pass

    def __getattr__(self, name):
        try:
            _name = name.split(self._data_items_prefix)[1]
        except IndexError:
            raise AttributeError
        else:
            return getattr(self.data, _name)


class ActionLog:
    """
    Append-only event log of action event
    """

    def __init__(
            self,
            file_path: str,
            data_class: Type[CsvSerializer] = ActionLogData,
            event_types: Type[Enum] = ActionLogEvents,
            delimiter: str ='\t'
    ):
        self._delimiter = delimiter
        self._file_path = file_path
        self._items = []
        self._data_class = data_class
        self._event_types = event_types
        self._load()

        for ev_type in self._event_types:
            setattr(self, "append_{}".format(ev_type.name),
                    functools.partial(self._append, ev_type))

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def delimiter(self) -> str:
        return self._delimiter

    @property
    def last_event(self) -> ActionLogEvent:
        return self._items[-1] if self._items else None

    @property
    def event_types(self) -> Enum:
        return self._event_types

    def _load(self):
        if os.path.exists(self._file_path):
            with open(self._file_path, mode='r', newline='') as f:
                for line in f:
                    self._items.append(ActionLogEvent.unpack(
                        line,
                        delimiter=self._delimiter,
                        data_class=self._data_class,
                        types=self._event_types
                    ))

    def _append(self, ev_type: Enum, data: ActionLogData) -> None:
        """
        Appends event to log
        Be careful it opens file every time!
        """
        event = ActionLogEvent(None, ev_type, data, types=self._event_types)
        with open(self._file_path, mode='a+', newline='') as f:
            f.write(event.pack(delimiter=self._delimiter))
        self._items.append(event)

    def __iter__(self):
        for item in self._items:
            yield item

    def __len__(self):
        return len(self._items)
