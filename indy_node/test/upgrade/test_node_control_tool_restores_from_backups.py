import multiprocessing
import os
import functools
import shutil

import time

from stp_core.loop.eventually import eventually
from indy_node.test.upgrade.helper import NodeControlToolExecutor as NCT, \
    sendUpgradeMessage, nodeControlGeneralMonkeypatching
from indy_node.server.upgrader import Upgrader

m = multiprocessing.Manager()
whitelist = ['Unexpected error in _upgrade test']


def testNodeControlRestoresFromBackups(monkeypatch, tdir, looper, tconf):
    msg = 'test'
    stdout = 'teststdout'
    currentVersion = Upgrader.getVersion()
    backupWasRestored = m.Value('b', False)
    testFile = 'testFile'
    original_text = '1'
    new_text = '2'

    def testRestoreBackup(tool, version):
        tool._restore_from_backup_test(version)
        backupWasRestored.value = True

    def mockMigrate(tool, *args):
        monkeypatch.setattr(tool, '_migrate', lambda *args: None)
        with open(os.path.join(tool.indy_dir, testFile), 'w') as f:
            f.write(new_text)
        raise Exception('test')

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        tool._restore_from_backup_test = tool._restore_from_backup
        monkeypatch.setattr(
            tool, '_migrate', functools.partial(mockMigrate, tool))
        monkeypatch.setattr(tool, '_restore_from_backup',
                            functools.partial(testRestoreBackup, tool))

    def checkBackupRestored(tool):
        assert backupWasRestored.value

    nct = NCT(backup_dir=tdir, backup_target=tdir, transform=transform)
    try:
        with open(os.path.join(nct.tool.indy_dir, testFile), 'w') as f:
            f.write(original_text)
        sendUpgradeMessage(msg)
        looper.run(eventually(checkBackupRestored, nct.tool))
        with open(os.path.join(nct.tool.indy_dir, testFile)) as f:
            assert original_text == f.read()
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