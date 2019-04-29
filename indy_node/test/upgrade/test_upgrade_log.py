import pytest
import os
import datetime

from common.version import SemVerReleaseVersion

import indy_common
from indy_node.server.upgrade_log import UpgradeLogData, UpgradeLog


@pytest.fixture
def log_file_path(tdir, request):
    return os.path.join(
        tdir,
        "{}.upgrade_log".format(os.path.basename(request.node.nodeid))
    )


@pytest.fixture
def src_version_cls_patched(monkeypatch):
    monkeypatch.setattr(
        indy_common.version,
        'src_version_cls',
        lambda *_: SemVerReleaseVersion
    )


def test_upgrade_log_data_unpack_invalid_version():
    with pytest.raises(TypeError) as excinfo:
        UpgradeLogData(str(datetime.datetime.utcnow()), 123, 'some_id', 'some_pkg')
    assert "'version' should be 'SourceVersion' or 'str'" in str(excinfo.value)


def test_upgrade_log_data_pack_unpack():
    delimiter = '|'
    data = UpgradeLogData(datetime.datetime.utcnow(), '1.2.3', 'some_id', 'some_pkg')
    assert data == UpgradeLogData.unpack(
        data.pack(delimiter=delimiter), delimiter=delimiter
    )


# TODO actually it is already well tested in base calss ActionLog
@pytest.mark.parametrize('ev_type', UpgradeLog.Events)
def test_upgrade_log_append_api(log_file_path, ev_type):
    upgrade_log = UpgradeLog(log_file_path)
    ev_data = UpgradeLogData(datetime.datetime.utcnow(), '1.2.3', 'some_id', 'some_pkg')
    getattr(upgrade_log, "append_{}".format(ev_type.name))(ev_data)
    assert upgrade_log.last_event.data == ev_data
    assert upgrade_log.last_event.ev_type == ev_type


def test_upgrade_log_loads_legacy_data(monkeypatch, log_file_path):

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
        "{}\tscheduled\t2019-02-28 07:37:11+00:00\t1.6.83\t15513393820971606221\r\n".format(tss[0]) +
        "{}\tstarted\t2019-02-28 07:37:11+00:00\t1.6.83\t15513393820971606221\tindy-node\r\n".format(tss[1]) +
        "{}\tsucceeded\t2019-02-28 07:37:11+00:00\t1.6.83\t15513393820971606221\tindy-node\r\n".format(tss[2])
    )

    new_logs = (
        "{}\tscheduled\t2019-02-28 07:37:11+00:00\t1.6.83\t15513393820971606221\tindy-node\r\n".format(tss[0]) +
        "{}\tstarted\t2019-02-28 07:37:11+00:00\t1.6.83\t15513393820971606221\tindy-node\r\n".format(tss[1]) +
        "{}\tsucceeded\t2019-02-28 07:37:11+00:00\t1.6.83\t15513393820971606221\tindy-node\r\n".format(tss[2])
    )


    with open(log_file_path, 'w', newline='') as f:
        f.write(legacy_logs)
    upgrade_log_legacy = UpgradeLog(log_file_path)

    log_file_path_new = log_file_path + '_new'
    upgrade_log_new = UpgradeLog(log_file_path_new)

    for ev_index, ev in enumerate(upgrade_log_legacy):
        getattr(upgrade_log_new, 'append_' + ev.ev_type.name)(ev.data)

    with open(log_file_path_new, 'r', newline='') as f:
        new_logs_read = f.read()

    assert new_logs_read == new_logs
