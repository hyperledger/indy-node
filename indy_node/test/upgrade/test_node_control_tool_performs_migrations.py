import multiprocessing
import os

import pytest

from stp_core.loop.eventually import eventually
from indy_common.constants import APP_NAME
from indy_common.version import src_version_cls
from indy_node.utils.migration_tool import _get_current_platform
from indy_node.utils.node_control_utils import NodeControlUtil, DebianVersion

from indy_node.test.upgrade.helper import (
    NodeControlToolExecutor as NCT,
    sendUpgradeMessage,
    nodeControlGeneralMonkeypatching,
    releaseVersion,
    bumpedVersion
)

m = multiprocessing.Manager()
# TODO why do we expect that
whitelist = ['Unexpected error in _upgrade test']


@pytest.fixture(scope='module')
def tconf(tconf, tdir):
    tconf.LOG_DIR = tdir
    yield tconf


def testNodeControlPerformsMigrations(monkeypatch, tdir, looper, tconf):
    version = bumpedVersion()
    stdout = 'teststdout'
    migrationFile = 'migrationProof'
    migrationText = "{} {}".format(releaseVersion(), version)

    old_call_upgrade_script = None

    def mock_call_upgrade_script(*args, **kwargs):
        old_call_upgrade_script(*args, **kwargs)
        monkeypatch.setattr(
            NodeControlUtil,
            '_get_curr_info',
            lambda *x, **y: (
                "Package: {}\nVersion: {}\n".format(APP_NAME, version)
            )
        )

    def mock_migrate(curr_src_ver: str, new_src_ver: str):
        with open(os.path.join(tdir, migrationFile), 'w') as f:
            f.write("{} {}".format(curr_src_ver, new_src_ver))

    def transform(tool):
        nonlocal old_call_upgrade_script
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        monkeypatch.setattr(tool, '_do_migration', mock_migrate)
        old_call_upgrade_script = getattr(tool, '_call_upgrade_script')
        monkeypatch.setattr(tool, '_call_upgrade_script', mock_call_upgrade_script)

    def checkMigration():
        with open(os.path.join(tdir, migrationFile)) as f:
            assert f.read() == migrationText

    monkeypatch.setattr(
        NodeControlUtil, 'get_latest_pkg_version',
        lambda *x, **y: DebianVersion(
            version, upstream_cls=src_version_cls())
    )

    nct = NCT(backup_dir=tdir, backup_target=tdir, transform=transform, config=tconf)
    try:
        sendUpgradeMessage(version)
        looper.run(eventually(checkMigration))
    finally:
        nct.stop()


def test_get_current_platform():
    _get_current_platform()
