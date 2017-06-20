import pytest
import multiprocessing
import os
import functools

import scripts.migration_tool as migration_tool
from stp_core.loop.eventually import eventually
from sovrin_node.test.upgrade.helper import NCT, composeUpgradeMessage, sendUpgradeMessage, nodeControlGeneralMonkeypatching
from sovrin_node.server.upgrader import Upgrader


m = multiprocessing.Manager()


def testNodeControlReceivesMessages(monkeypatch):
    received = m.list()
    msg = 'test'

    def transform(tool):
        monkeypatch.setattr(tool, '_process_data', received.append)

    nct = NCT(transform = transform)
    try:
        sendUpgradeMessage(msg)
        assert len(received) == 1
        assert received[0] == composeUpgradeMessage(msg)
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
    current_version = Upgrader.getVersion()

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        monkeypatch.setattr(tool, '_remove_backup', lambda *x: None)

    def checkBackup(tool):
        assert os.path.isfile('{}.{}'.format(tool._backup_name(current_version), tool.backup_format))
    nct = NCT(transform = transform)
    try:
        sendUpgradeMessage(msg)
        looper.run(eventually(checkBackup, nct.tool))
    finally:
        nct.stop()


def testNodeControlRemovesBackups(monkeypatch, tdir, looper):
    msg = 'test'
    stdout = 'teststdout'
    current_version = Upgrader.getVersion()
    backup_was_removed = m.Value('b', False)

    def testRemoveBackup(tool, version):
        backup_was_removed.value = True
        tool._remove_backup_test(version)

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        tool._remove_backup_test = tool._remove_backup
        monkeypatch.setattr(tool, '_remove_backup', functools.partial(testRemoveBackup, tool))

    def checkBackupRemoved(tool):
        assert backup_was_removed.value

    nct = NCT(transform = transform)
    try:
        sendUpgradeMessage(msg)
        looper.run(eventually(checkBackupRemoved, nct.tool))
        assert not os.path.exists('{}.{}'.format(nct.tool._backup_name(current_version), nct.tool.backup_format))
    finally:
        nct.stop()

