import pytest
import multiprocessing
import os
import functools
import shutil

from stp_core.loop.eventually import eventually
from indy_node.test.upgrade.helper import NodeControlToolExecutor as NCT, composeUpgradeMessage, sendUpgradeMessage, nodeControlGeneralMonkeypatching
from indy_node.server.upgrader import Upgrader
from indy_node.utils.node_control_tool import NodeControlTool
from plenum.test.helper import randomText


m = multiprocessing.Manager()
whitelist = ['Unexpected error in _upgrade test']


def testNodeControlReceivesMessages(monkeypatch, looper, tdir):
    received = m.list()
    msg = 'test'
    stdout = 'teststdout'

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        monkeypatch.setattr(tool, '_process_data', received.append)

    def checkMessage():
        assert len(received) == 1
        assert received[0] == composeUpgradeMessage(msg)

    nct = NCT(backup_dir=tdir, backup_target=tdir, transform=transform)
    try:
        sendUpgradeMessage(msg)
        looper.run(eventually(checkMessage))
    finally:
        nct.stop()


def testNodeControlResolvesDependencies(monkeypatch):
    nct = NodeControlTool()
    node_package = ('indy-node', '0.0.1')
    anoncreds_package = ('indy-anoncreds', '0.0.2')
    plenum_package = ('indy-plenum', '0.0.3')
    node_package_with_version = '{}={}'.format(*node_package)
    plenum_package_with_version = '{}={}'.format(*plenum_package)
    anoncreds_package_with_version = '{}={}'.format(*anoncreds_package)
    mock_info = {
        node_package_with_version: '{}{} (= {}){}{} (= {}){}'.format(
            randomText(100),
            *plenum_package,
            randomText(100),
            *anoncreds_package,
            randomText(100)),
        plenum_package_with_version: '{}'.format(
            randomText(100)),
        anoncreds_package_with_version: '{}'.format(
            randomText(100))}

    def mock_get_info_from_package_manager(self, package):
        return mock_info.get(package, None)

    monkeypatch.setattr(nct.__class__, '_get_info_from_package_manager',
                        mock_get_info_from_package_manager)
    monkeypatch.setattr(
        nct.__class__, '_update_package_cache', lambda *x: None)
    ret = nct._get_deps_list(node_package_with_version)
    assert ret.split() == [
        anoncreds_package_with_version,
        plenum_package_with_version,
        node_package_with_version]


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

    nct = NCT(backup_dir=tdir, backup_target=tdir, transform=transform)
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


def testNodeControlRemovesBackups(monkeypatch, tdir, looper):
    msg = 'test'
    stdout = 'teststdout'
    currentVersion = Upgrader.getVersion()
    backupsWereRemoved = m.Value('b', False)

    def testRemoveOldBackups(tool):
        assert len(tool._get_backups()) == (tool.backup_num + 1)
        tool._remove_old_backups_test()
        backupsWereRemoved.value = True

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        tool._remove_old_backups_test = tool._remove_old_backups
        monkeypatch.setattr(tool, '_remove_old_backups',
                            functools.partial(testRemoveOldBackups, tool))

    def checkOldBackupsRemoved():
        assert backupsWereRemoved.value

    nct = NCT(backup_dir=tdir, backup_target=tdir, transform=transform)
    try:
        assert len(nct.tool._get_backups()) == 0
        for i in range(nct.tool.backup_num):
            file = os.path.join(nct.tool.base_dir, '{}{}'.format(
                nct.tool.backup_name_prefix, i))
            with open(file, 'w') as f:
                f.write('random')
        assert len(nct.tool._get_backups()) == nct.tool.backup_num
        sendUpgradeMessage(msg)
        looper.run(eventually(checkOldBackupsRemoved))
        assert os.path.exists('{}.{}'.format(
            nct.tool._backup_name(currentVersion), nct.tool.backup_format))
        assert len(nct.tool._get_backups()) == nct.tool.backup_num
    finally:
        clean_dir(nct.tool.base_dir)
        nct.stop()


def testNodeControlRestoresFromBackups(monkeypatch, tdir, looper):
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
