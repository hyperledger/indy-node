import pytest
import os
from datetime import datetime

from indy_node.server.action_log import ActionLogData, ActionLog


# TODO
# - test ActionLogData API
# - test ActionLogRecord API


class ActionTestLogData(ActionLogData):
    def __init__(self, when, f1: str, f2: int):
        super().__init__(when)
        self.f1 = f1
        self.f2 = f2

    @property
    def packed(self):
        return super().packed + [self.f1, str(self.f2)]

    @staticmethod
    def parse(when, f1, f2):
        return [ActionLogData.parse(when), f1, int(f2)]


class ActionTestLog(ActionLog):
    def __init__(self, *args, data_class=ActionTestLogData, **kwargs):
        super().__init__(*args, data_class=data_class, **kwargs)


@pytest.fixture(scope='module')
def action_log_delimiter(tdir, request):
    return '>'


@pytest.fixture
def action_log_file_path(tdir, request):
    return os.path.join(
        tdir,
        "{}.action_log".format(os.path.basename(request.node.nodeid))
    )


@pytest.fixture(scope='module')
def prepared_data():
    return [
        ActionTestLogData(datetime.utcnow(), '1', 1),
        ActionTestLogData(datetime.utcnow(), '2', 2),
        ActionTestLogData(datetime.utcnow(), '3', 3)
    ]


@pytest.fixture
def action_log(action_log_file_path, action_log_delimiter):
    return ActionTestLog(
        action_log_file_path, delimiter=action_log_delimiter)


@pytest.fixture
def action_log_prepared(action_log, prepared_data):
    for data in prepared_data:
        action_log.append_scheduled(data)
    return action_log


def test_action_log_api_basic(
        action_log_prepared, action_log_file_path,
        action_log_delimiter, prepared_data):

    # basic ones
    assert action_log_prepared.file_path == action_log_file_path
    assert action_log_prepared.delimiter == action_log_delimiter
    assert len(action_log_prepared) == len(prepared_data)
    for rec, data in zip(action_log_prepared, prepared_data):
        assert rec.ev_data == data
    assert action_log_prepared.last_event.ev_data == prepared_data[-1]

    # helpers for append
    for ev_type in ActionLog.Events:
        assert hasattr(action_log_prepared, "append_{}".format(ev_type.name))


@pytest.mark.parametrize(
    'ev_type', ActionLog.Events, ids=lambda ev: ev.name)
def test_action_log_append(action_log, ev_type):
    ev_data = ActionTestLogData(datetime.utcnow(), '1', 2)
    getattr(action_log, "append_{}".format(ev_type.name))(ev_data)
    assert action_log.last_event.ev_data == ev_data
    assert action_log.last_event.ev_type == ev_type


def test_action_log_append_with_args(action_log):
    args = (datetime.utcnow(), '1', 2)
    action_log.append_scheduled(*args)
    assert action_log.last_event.ev_data == ActionTestLogData(*args)


def test_action_log_write_file(action_log):
    ev_data = ActionTestLogData(datetime.utcnow(), '1', 2)

    def check_log(expected):
        num_lines = -1
        with open(action_log.file_path, 'r') as _f:
            for num_lines, _ in enumerate(_f):
                pass
        assert (num_lines + 1) == expected

    action_log.append_scheduled(ev_data)
    check_log(1)
    action_log.append_started(ev_data)
    check_log(2)
    action_log.append_cancelled(ev_data)
    check_log(3)


def test_action_log_load(action_log_prepared):
    new_log = ActionTestLog(
        action_log_prepared.file_path,
        delimiter=action_log_prepared.delimiter)

    assert len(action_log_prepared) == len(new_log)
    for rec1, rec2 in zip(action_log_prepared, new_log):
        assert rec1 == rec2
