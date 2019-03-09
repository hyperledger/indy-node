import multiprocessing
import os
import functools
import shutil

import time

from stp_core.loop.eventually import eventually
from indy_common.version import src_version_cls
from indy_node.server.upgrader import Upgrader
from indy_node.utils.node_control_utils import NodeControlUtil, DebianVersion

from indy_node.test.upgrade.helper import (
    NodeControlToolExecutor as NCT,
    sendUpgradeMessage,
    nodeControlGeneralMonkeypatching,
    bumpedVersion
)

m = multiprocessing.Manager()
# TODO why do we expect that
whitelist = ['Unexpected error in _upgrade test']


def testNodeControlRestoresFromBackups(monkeypatch, tdir, looper, tconf):
    version = bumpedVersion()
    stdout = 'teststdout'
    backupWasRestored = m.Value('b', False)
    testFile = 'testFile'
    original_text = '1'
    new_text = '2'

    def testRestoreBackup(tool, src_ver: str):
        tool._restore_from_backup_test(src_ver)
        backupWasRestored.value = True

    def mockMigrate(tool, *args):
        monkeypatch.setattr(tool, '_do_migration', lambda *args: None)
        with open(os.path.join(tool.indy_dir, testFile), 'w') as f:
            f.write(new_text)
        raise Exception('test')

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        tool._restore_from_backup_test = tool._restore_from_backup
        monkeypatch.setattr(
            tool, '_do_migration', functools.partial(mockMigrate, tool))
        monkeypatch.setattr(tool, '_restore_from_backup',
                            functools.partial(testRestoreBackup, tool))

    def checkBackupRestored(tool):
        assert backupWasRestored.value

    monkeypatch.setattr(
        NodeControlUtil, 'get_latest_pkg_version',
        lambda *x, **y: DebianVersion(
            version, upstream_cls=src_version_cls())
    )

    nct = NCT(backup_dir=tdir, backup_target=tdir, transform=transform)
    try:
        with open(os.path.join(nct.tool.indy_dir, testFile), 'w') as f:
            f.write(original_text)
        sendUpgradeMessage(version)
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
