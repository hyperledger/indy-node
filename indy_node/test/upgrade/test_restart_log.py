import pytest
import os

from indy_node.server.restart_log import RestartLog, RestartLogData
import datetime

@pytest.fixture
def log_file_path(tdir, request):
    return os.path.join(
        tdir,
        "{}.restart_log".format(os.path.basename(request.node.nodeid))
    )


def test_restart_log_data_pack_unpack():
    delimiter = '|'
    data = RestartLogData(datetime.datetime.utcnow())
    assert data == RestartLogData.unpack(
        data.pack(delimiter=delimiter), delimiter=delimiter
    )



# TODO actually it is already well tested in base calss ActionLog
@pytest.mark.parametrize('ev_type', RestartLog.Events)
def test_restart_log_append_api(log_file_path, ev_type):
    restart_log = RestartLog(log_file_path)
    ev_data = RestartLogData(datetime.datetime.utcnow())
    getattr(restart_log, "append_{}".format(ev_type.name))(ev_data)
    assert restart_log.last_event.data == ev_data
    assert restart_log.last_event.ev_type == ev_type


def test_restart_log_loads_legacy_data(monkeypatch, log_file_path):

    ev_index = None
    tss = [
        '2019-02-28 07:36:23.135789',
        '2019-02-28 07:37:11.008484',
        '2019-02-28 07:38:33.721644'
    ]

    class datetime_wrapper(datetime.datetime):
        def utcnow():
            return tss[ev_index]

    monkeypatch.setattr(datetime, 'datetime', datetime_wrapper)

    legacy_logs = (
        "{}\tscheduled\t2019-02-28 07:37:11+00:00\r\n".format(tss[0]) +
        "{}\tstarted\t2019-02-28 07:37:11+00:00\r\n".format(tss[1]) +
        "{}\tsucceeded\t2019-02-28 07:37:11+00:00\r\n".format(tss[2])
    )

    with open(log_file_path, 'w', newline='') as f:
        f.write(legacy_logs)
    restart_log_legacy = RestartLog(log_file_path)

    log_file_path_new = log_file_path + '_new'
    restart_log_new = RestartLog(log_file_path_new)

    for ev_index, ev in enumerate(restart_log_legacy):
        getattr(restart_log_new, 'append_' + ev.ev_type.name)(ev.data)

    with open(log_file_path_new, 'r', newline='') as f:
        new_logs = f.read()

    assert legacy_logs == new_logs
