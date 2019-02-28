import pytest
import os
from datetime import datetime
from dateutil.parser import parse as parse_dt
from enum import Enum, unique

from indy_node.server.action_log import (
    CsvSerializer,
    ActionLogEvents, ActionLogData, ActionLogEvent, ActionLog,
)

# TODO
# - check specific error messages for expected exceptions
# - try to load current logs
# - move csv serializer tests to separate module


class LogDataParent(CsvSerializer):
    _items = ['f1']

    def __init__(self, f1):
        self.f1 = f1


class LogData(LogDataParent):
    _items = LogDataParent._items + ['f2']

    def __init__(self, f1, f2):
        super().__init__(f1)
        self.f2 = int(f2)


@unique
class Events(Enum):
    eventA = 1
    eventB = 2
    eventC = 3

    def __str__(self):
        return self.name


class ActionTestLog(ActionLog):

    Events = Events

    """
    Append-only event log of upgrade event
    """
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            data_class=LogData,
            event_types=Events,
            **kwargs
        )


# FIXTURES


@pytest.fixture
def valid_ts():
    return datetime.utcnow()


@pytest.fixture(scope='module')
def valid_event():
    return Events.eventA


@pytest.fixture(scope='module')
def valid_data():
    return LogData('1', 2)


@pytest.fixture(scope='module')
def log_delimiter(tdir, request):
    return '>'


@pytest.fixture
def log_file_path(tdir, request):
    return os.path.join(
        tdir,
        "{}.action_log".format(os.path.basename(request.node.nodeid))
    )


@pytest.fixture(scope='module')
def prepared_data():
    return [
        LogData('1', 1),
        LogData('2', 2),
        LogData('3', 3)
    ]


@pytest.fixture
def action_log(log_file_path, log_delimiter):
    return ActionTestLog(log_file_path, delimiter=log_delimiter)


@pytest.fixture
def action_log_prepared(action_log, prepared_data):
    for data in prepared_data:
        action_log.append_eventB(data)
    return action_log


class CsvSerializerTest(CsvSerializer):
    _items = ['int_', 'ts', 'str_']

    def __init__(self, int_, ts, str_, *args, **kwargs):
        self.int_ = int(int_)
        self.ts = parse_dt(ts)
        self.str_ = str_
        self.args = args
        self.kwargs = kwargs

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other


@pytest.fixture(scope='module')
def test_obj():
    return CsvSerializerTest('1', str(datetime.utcnow()), 'qwerty')


# TESTS


def test_csv_serializer_iter(test_obj):
    assert list(iter(test_obj)) == [test_obj.int_, test_obj.ts, test_obj.str_]


def test_csv_serializer_pack_unpack():
    delimiter = '_'
    args = (5,)
    kwargs = {'kw': 6}
    test_obj = CsvSerializerTest(
        '1', str(datetime.utcnow()), 'qwerty', *args, **kwargs
    )
    assert test_obj == CsvSerializerTest.unpack(
        test_obj.pack(delimiter=delimiter), *args, delimiter=delimiter, **kwargs
    )


def test_action_log_data_init(valid_ts):
    assert ActionLogData(valid_ts).when == valid_ts
    assert ActionLogData(valid_ts.isoformat()).when == valid_ts
    assert ActionLogData(str(valid_ts)).when == valid_ts
    with pytest.raises(TypeError):
        ActionLogData(123)


def test_action_log_event_init_invalid_ts(valid_ts, valid_event):
    with pytest.raises(TypeError):
        ActionLogEvent(
            123, valid_event, ActionLogData(datetime.utcnow()),
        )


def test_action_log_event_init_valid_ts_none(valid_event, valid_data):
    ts1 = datetime.utcnow()
    ev = ActionLogEvent(None, valid_event, valid_data, types=Events)
    ts2 = datetime.utcnow()
    # a kind of non-strict check
    assert ts1 <= ev.ts <= ts2


def test_action_log_event_init_valid_ts_datetime(
        valid_ts, valid_event, valid_data):
    ev = ActionLogEvent(valid_ts, valid_event, valid_data, types=Events)
    assert ev.ts == valid_ts


def test_action_log_event_init_valid_ts_str(
        valid_ts, valid_event, valid_data):
    ev = ActionLogEvent(valid_ts.isoformat(), valid_event,
                        valid_data, types=Events)
    assert ev.ts == valid_ts


def test_action_log_event_init_invalid_ev_type(valid_ts, valid_data):
    _Events = Enum('_Events', 'ev1 ev2 ev3')

    # unexpected type
    with pytest.raises(TypeError):
        ActionLogEvent(valid_ts, 123, valid_data, types=_Events)

    # unexpected event name
    with pytest.raises(ValueError):
        ActionLogEvent(valid_ts, 'ev4', valid_data, types=_Events)

    # unexpected event
    with pytest.raises(ValueError):
        ActionLogEvent(
            valid_ts, Enum('_Events', 'ev1 ev2 ev3')['ev1'],
            valid_data, types=_Events
        )


def test_action_log_event_init_valid_ev_type(valid_ts, valid_data):
    _Events = Enum('_Events', 'ev1 ev2 ev3')

    assert ActionLogEvent(
        valid_ts, 'ev2', valid_data, types=_Events
    ).ev_type == _Events.ev2

    assert ActionLogEvent(
        valid_ts, _Events.ev3, valid_data, types=_Events
    ).ev_type == _Events.ev3


def test_action_log_event_init_invalid_data(valid_ts, valid_event):
    # data_class is not specified and data not an instance of CsvSerializer
    with pytest.raises(TypeError):
        ActionLogEvent(valid_ts, valid_event, valid_ts, types=Events)

    # data_class is specified but it's not a CsvSerializer child
    with pytest.raises(TypeError):
        ActionLogEvent(
            valid_ts, valid_event, 'any_value', types=Events,
            data_class=type("SomeClass", (), {'__init__': lambda *_: None})
        )


def test_action_log_event_init_valid_data(valid_ts, valid_event, valid_data):
    assert ActionLogEvent(
        valid_ts, valid_event, valid_data, types=Events
    ).data == valid_data


def test_action_log_event_init_data_class_passed(valid_ts, valid_event):

    class SomeClass(CsvSerializer):
        _items = ['item1', 'item2', 'item3']

        def __init__(self, *args):
            for idx, v in enumerate(args):
                setattr(self, "item" + str(idx), v)

    ev = ActionLogEvent(
        valid_ts, valid_event, '_item1', '_item2', '_item3',
        types=Events, data_class=SomeClass
    )

    ev.data == SomeClass('_item1', '_item2', '_item3')


def test_action_log_event_pack_unpack(valid_ts, valid_event, valid_data):
    delimiter = '|'
    ev = ActionLogEvent(valid_ts, valid_event, valid_data, types=Events)
    assert ev == ActionLogEvent.unpack(
        ev.pack(delimiter=delimiter), delimiter=delimiter,
        data_class=LogData, types=Events)


def test_action_log_api_basic(
        action_log_prepared, log_file_path,
        log_delimiter, prepared_data):

    # basic ones
    assert action_log_prepared.file_path == log_file_path
    assert action_log_prepared.delimiter == log_delimiter
    assert len(action_log_prepared) == len(prepared_data)
    for ev, data in zip(action_log_prepared, prepared_data):
        assert ev.data == data
    assert action_log_prepared.last_event.data == prepared_data[-1]

    # helpers for append
    for ev_type in Events:
        assert hasattr(action_log_prepared, "append_{}".format(ev_type.name))


@pytest.mark.parametrize('ev_type', Events)
def test_action_log_append(action_log, ev_type):
    ev_data = LogData('1', 2)
    getattr(action_log, "append_{}".format(ev_type.name))(ev_data)
    assert action_log.last_event.data == ev_data
    assert action_log.last_event.ev_type == ev_type


def test_action_log_write_file(action_log):
    ev_data = LogData('1', 2)

    def check_log(expected):
        num_lines = -1
        with open(action_log.file_path, 'r') as _f:
            for num_lines, _ in enumerate(_f):
                pass
        assert (num_lines + 1) == expected

    action_log.append_eventA(ev_data)
    check_log(1)
    action_log.append_eventB(ev_data)
    check_log(2)
    action_log.append_eventC(ev_data)
    check_log(3)


def test_action_log_load(action_log_prepared):
    new_log = ActionTestLog(
        action_log_prepared.file_path,
        delimiter=action_log_prepared.delimiter
    )

    assert len(action_log_prepared) == len(new_log)
    for ev1, ev2 in zip(action_log_prepared, new_log):
        assert ev1 == ev2
