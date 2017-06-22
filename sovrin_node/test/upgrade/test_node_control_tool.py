import pytest
import multiprocessing
import os
import functools

from stp_core.loop.eventually import eventually
from sovrin_node.test.upgrade.helper import NodeControlToolExecutor as NCT, composeUpgradeMessage, sendUpgradeMessage, nodeControlGeneralMonkeypatching
from sovrin_node.server.upgrader import Upgrader


m = multiprocessing.Manager()


def testNodeControlReceivesMessages(monkeypatch, looper):
    received = m.list()
    msg = 'test'

    def transform(tool):
        monkeypatch.setattr(tool, '_process_data', received.append)

    def checkMessage():
        assert len(received) == 1
        assert received[0] == composeUpgradeMessage(msg)

    nct = NCT(transform = transform)
    try:
        sendUpgradeMessage(msg)
        looper.run(eventually(checkMessage))
    finally:
        nct.stop()


def testNodeControlPerformsMigrations(monkeypatch, tdir, looper):
    msg = 'test'
    stdout = 'teststdout'
    migrationFile = 'migrationProof'
    migrationText = 'testMigrations'

    def mock_migrate(*args):
        with open(os.path.join(tdir, migrationFile), 'w') as f:
            f.write(migrationText)

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        monkeypatch.setattr(tool, '_migrate', mock_migrate)

    def checkMigration():
        with open(os.path.join(tdir, migrationFile)) as f:
            assert f.read() == migrationText

    nct = NCT(transform = transform)
    try:
        sendUpgradeMessage(msg)
        looper.run(eventually(checkMigration))
    finally:
        nct.stop()


def testNodeControlCreatesBackups(monkeypatch, tdir, looper):
    msg = 'test'
    stdout = 'teststdout'
    currentVersion = Upgrader.getVersion()

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        monkeypatch.setattr(tool, '_remove_backup', lambda *x: None)

    def checkBackup(tool):
        assert os.path.isfile('{}.{}'.format(tool._backup_name(currentVersion), tool.backup_format))
    nct = NCT(transform = transform)
    try:
        sendUpgradeMessage(msg)
        looper.run(eventually(checkBackup, nct.tool))
    finally:
        nct.stop()


def testNodeControlRemovesBackups(monkeypatch, tdir, looper):
    msg = 'test'
    stdout = 'teststdout'
    currentVersion = Upgrader.getVersion()
    backupWasRemoved = m.Value('b', False)

    def testRemoveBackup(tool, version):
        backupWasRemoved.value = True
        tool._remove_backup_test(version)

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        tool._remove_backup_test = tool._remove_backup
        monkeypatch.setattr(tool, '_remove_backup', functools.partial(testRemoveBackup, tool))

    def checkBackupRemoved(tool):
        assert backupWasRemoved.value

    nct = NCT(transform = transform)
    try:
        sendUpgradeMessage(msg)
        looper.run(eventually(checkBackupRemoved, nct.tool))
        assert not os.path.exists('{}.{}'.format(nct.tool._backup_name(currentVersion), nct.tool.backup_format))
    finally:
        nct.stop()


def testNodeControlRestoresFromBackups(monkeypatch, tdir, looper):
    msg = 'test'
    stdout = 'teststdout'
    currentVersion = Upgrader.getVersion()
    backupWasRestored = m.Value('b', False)
    testFile = 'testFile'

    def testRestoreBackup(tool, version):
        backupWasRestored.value = True
        tool._restore_from_backup_test(version)

    def mockMigrate(tool):
        with open(os.path.join(tool.sovrin_dir, testFile), 'w') as f:
            f.write('random')
        raise Exception('test')

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        tool._restore_from_backup_test = tool._restore_from_backup
        monkeypatch.setattr(tool, '_migrate', functools.partial(mockMigrate, tool))
        monkeypatch.setattr(tool, '_restore_from_backup', functools.partial(testRestoreBackup, tool))

    def checkBackupRestored(tool):
        assert backupWasRestored.value

    nct = NCT(transform = transform)
    try:
        sendUpgradeMessage(msg)
        looper.run(eventually(checkBackupRestored, nct.tool))
        assert not os.path.exists(os.path.join(nct.tool.sovrin_dir, testFile))
    finally:
        nct.stop()

