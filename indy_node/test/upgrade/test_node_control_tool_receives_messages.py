import multiprocessing
from stp_core.loop.eventually import eventually
from indy_node.test.upgrade.helper import NodeControlToolExecutor as NCT, \
    composeUpgradeMessage, sendUpgradeMessage, nodeControlGeneralMonkeypatching



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