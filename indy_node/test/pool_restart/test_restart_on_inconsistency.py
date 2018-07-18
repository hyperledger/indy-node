import multiprocessing

from indy_node.test.upgrade.helper import NodeControlToolExecutor, nodeControlGeneralMonkeypatching
from stp_core.loop.eventually import eventually


def test_restart_on_inconsistency(looper, txnPoolNodeSet, tdir, monkeypatch):
    restarted = multiprocessing.Value('i', 0)

    def notify_restart():
        with restarted.get_lock():
            restarted.value = 1

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, 'teststdout')
        monkeypatch.setattr(tool, '_restart', notify_restart)

    def check_restart():
        with restarted.get_lock():
            assert restarted.value == 1

    nct = NodeControlToolExecutor(backup_dir=tdir, backup_target=tdir, transform=transform)
    try:
        txnPoolNodeSet[0].on_inconsistent_3pc_state()
        looper.run(eventually(check_restart))
    finally:
        nct.stop()


