import multiprocessing
import os
import shutil

from stp_core.loop.eventually import eventually
from indy_node.test.upgrade.helper import NodeControlToolExecutor as NCT, sendUpgradeMessage, nodeControlGeneralMonkeypatching
from indy_node.server.upgrader import Upgrader

m = multiprocessing.Manager()
whitelist = ['Unexpected error in _upgrade test']

def testNodeControlCreatesBackups(monkeypatch, tdir, looper):
    msg = 'test'
    stdout = 'teststdout'
    currentVersion = Upgrader.getVersion()

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        monkeypatch.setattr(tool, '_remove_old_backups', lambda *x: None)

    def checkBackup(tool):
        assert os.path.isfile('{}.{}'.format(
            tool._backup_name(currentVersion), tool.backup_format))

    nct = NCT(backup_dir=tdir, backup_target=tdir, transform=transform)
    try:
        sendUpgradeMessage(msg)
        looper.run(eventually(checkBackup, nct.tool))
    finally:
        clean_dir(nct.tool.base_dir)
        nct.stop()

def clean_dir(dir):
    for file in os.listdir(dir):
        file = os.path.join(dir, file)
        if os.path.isfile(file):
            os.remove(file)
        if os.path.isdir(file):
            shutil.rmtree(file, ignore_errors=True)