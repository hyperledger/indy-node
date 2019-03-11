import multiprocessing
from stp_core.loop.eventually import eventually
from indy_common.version import src_version_cls
from indy_node.utils.node_control_utils import NodeControlUtil, DebianVersion

from indy_node.test.upgrade.helper import (
    NodeControlToolExecutor as NCT,
    composeUpgradeMessage,
    sendUpgradeMessage,
    nodeControlGeneralMonkeypatching,
    bumpedVersion
)


m = multiprocessing.Manager()
# TODO why do we expect that
whitelist = ['Unexpected error in _upgrade test']


def testNodeControlReceivesMessages(monkeypatch, looper, tdir, tconf):
    received = m.list()
    version = bumpedVersion()
    stdout = 'teststdout'

    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout)
        monkeypatch.setattr(tool, '_process_data', received.append)

    def checkMessage():
        assert len(received) == 1
        assert received[0] == composeUpgradeMessage(version)

    monkeypatch.setattr(
        NodeControlUtil, 'get_latest_pkg_version',
        lambda *x, **y: DebianVersion(
            version, upstream_cls=src_version_cls())
    )

    nct = NCT(backup_dir=tdir, backup_target=tdir, transform=transform)
    try:
        sendUpgradeMessage(version)
        looper.run(eventually(checkMessage))
    finally:
        nct.stop()
