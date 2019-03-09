import multiprocessing
import os
import shutil

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

def testNodeControlCreatesBackups(monkeypatch, tdir, looper, tconf):
    version = bumpedVersion()
    stdout = 'teststdout'
    curr_src_ver = Upgrader.get_src_version()

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        monkeypatch.setattr(tool, '_remove_old_backups', lambda *x: None)

    def checkBackup(tool):
        assert os.path.isfile('{}.{}'.format(
            tool._backup_name(curr_src_ver.release), tool.backup_format))

    monkeypatch.setattr(
        NodeControlUtil, 'get_latest_pkg_version',
        lambda *x, **y: DebianVersion(
            version, upstream_cls=src_version_cls())
    )

    nct = NCT(backup_dir=tdir, backup_target=tdir, transform=transform)
    try:
        sendUpgradeMessage(version)
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
