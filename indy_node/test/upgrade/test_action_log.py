import pytest
import os
from datetime import datetime

from indy_node.server.action_log import ActionLogData, ActionLog


# TODO
# - test ActionLogData API
# - test ActionLogRecord API
#


class ActionTestLogData(ActionLogData):
    def __init__(self, when, f1: str, f2: int):
        super().__init__(when)
        self.f1 = f1
        self.f2 = f2

    @property
    def packed(self):
        return list(super().packed) + [self.f1, str(self.f2)]

    @staticmethod
    def parse(when, f1, f2):
        return [ActionLogData.parse(when), f1, int(f2)]


class ActionTestLog(ActionLog):
    def __init__(self, filePath, delimiter="\t"):
        super().__init__(
            filePath, data_class=ActionTestLogData, delimiter=delimiter)


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


def test_action_log_api(
        action_log_prepared, action_log_file_path,
        action_log_delimiter, prepared_data):

    # basic ones
    assert action_log_prepared.file_path == action_log_file_path
    assert action_log_prepared.delimiter == action_log_delimiter
    assert len(action_log_prepared) == len(prepared_data)
    for rec, data in zip(action_log_prepared, prepared_data):
        assert rec.ev_data == data
    assert action_log_prepared.lastEvent.ev_data == prepared_data[-1]

    # helpers for append
    for ev_type in ActionLog.Events:
        assert hasattr(action_log_prepared, "append_{}".format(ev_type.name))


def test_action_log_write(action_log):
    ev_data = ActionTestLogData(datetime.utcnow(), '1', 2)
    action_log.append_scheduled(ev_data)
    assert action_log.lastEvent.ev_data == ev_data
    # TODO check that it has been written to file


def test_action_log_load(action_log_prepared):
    new_log = ActionTestLog(
        action_log_prepared.file_path, action_log_prepared.delimiter)

    assert len(action_log_prepared) == len(new_log)
    for rec1, rec2 in zip(action_log_prepared, new_log):
        assert rec1 == rec2
