import multiprocessing
import os
import functools
import shutil

from stp_core.loop.eventually import eventually
from stp_core.common.log import getlogger

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
logger = getlogger()


def testNodeControlRemovesBackups(monkeypatch, tdir, looper, tconf):
    version = bumpedVersion()
    stdout = 'teststdout'
    curr_src_ver = Upgrader.get_src_version()
    backupsWereRemoved = m.Value('b', False)

    def testRemoveOldBackups(tool):
        assert len(tool._get_backups()) == (tool.backup_num + 1)
        #looper = Looper(debug=True)
        tool._remove_old_backups_test()
        backupsWereRemoved.value = True

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        tool._remove_old_backups_test = tool._remove_old_backups
        monkeypatch.setattr(tool, '_remove_old_backups',
                            functools.partial(testRemoveOldBackups, tool))

    def checkOldBackupsRemoved():
        assert backupsWereRemoved.value

    def check_backups_files_exists():
        assert os.path.exists('{}.{}'.format(
            nct.tool._backup_name(curr_src_ver.release), nct.tool.backup_format))

    monkeypatch.setattr(
        NodeControlUtil, 'get_latest_pkg_version',
        lambda *x, **y: DebianVersion(
            version, upstream_cls=src_version_cls())
    )

    nct = NCT(backup_dir=tdir, backup_target=tdir, transform=transform)
    try:
        assert len(nct.tool._get_backups()) == 0
        for i in range(nct.tool.backup_num):
            file = os.path.join(nct.tool.base_dir, '{}{}'.format(
                nct.tool.backup_name_prefix, i))
            with open(file, 'w') as f:
                f.write('random')
        assert len(nct.tool._get_backups()) == nct.tool.backup_num
        sendUpgradeMessage(version)
        looper.run(eventually(checkOldBackupsRemoved))
        looper.run(eventually(check_backups_files_exists))
        assert len(nct.tool._get_backups()) == nct.tool.backup_num
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
