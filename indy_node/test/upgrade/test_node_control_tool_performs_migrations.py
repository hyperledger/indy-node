import multiprocessing
import os

from stp_core.loop.eventually import eventually
from indy_node.test.upgrade.helper import NodeControlToolExecutor as NCT, sendUpgradeMessage, nodeControlGeneralMonkeypatching



m = multiprocessing.Manager()
whitelist = ['Unexpected error in _upgrade test']

def testNodeControlPerformsMigrations(monkeypatch, tdir, looper, tconf):
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