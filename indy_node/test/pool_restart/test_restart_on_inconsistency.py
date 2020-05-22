import multiprocessing

import pytest

from indy_node.test.upgrade.helper import NodeControlToolExecutor, nodeControlGeneralMonkeypatching
from stp_core.loop.eventually import eventually

RESTART_TIMEOUT = 10


@pytest.fixture(scope="module")
def tconf(tconf, tdir):
    old_restart_timeout = tconf.INCONSISTENCY_WATCHER_NETWORK_TIMEOUT
    tconf.INCONSISTENCY_WATCHER_NETWORK_TIMEOUT = RESTART_TIMEOUT
    tconf.LOG_DIR = tdir
    yield tconf
    tconf.INCONSISTENCY_WATCHER_NETWORK_TIMEOUT = old_restart_timeout


def test_restart_on_inconsistency(looper, txnPoolNodeSet, tconf, tdir, monkeypatch):
    restarted = multiprocessing.Value('i', 0)

    def notify_restart():
        with restarted.get_lock():
            restarted.value = 1

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, 'teststdout')
        monkeypatch.setattr(tool, '_restart', notify_restart)

    def check_restart(value):
        with restarted.get_lock():
            assert restarted.value == value

    nct = NodeControlToolExecutor(backup_dir=tdir, backup_target=tdir, transform=transform, config=tconf)
    try:
        # Trigger inconsistent 3PC state event
        txnPoolNodeSet[0].on_inconsistent_3pc_state()

        # Ensure we don't restart before timeout
        looper.runFor(0.8 * RESTART_TIMEOUT)
        check_restart(0)

        # Ensure we restart eventually
        looper.run(eventually(check_restart, 1, retryWait=1.0))
    finally:
        nct.stop()


