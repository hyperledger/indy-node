from plenum.common.util import randomString
from stp_core.loop.eventually import eventually
from plenum.test.helper import waitForSufficientRepliesForRequests
from plenum.test import waits as plenumWaits
from sovrin_client.client.wallet.upgrade import Upgrade
from sovrin_node.server.upgrader import Upgrader
from sovrin_node.utils.node_control_tool import NodeControlTool
from sovrin_common.config_util import getConfig
import subprocess
import os
import multiprocessing
import socket
import json


config = getConfig()


def sendUpgrade(client, wallet, upgradeData):
    upgrade = Upgrade(**upgradeData, trustee=wallet.defaultId)
    wallet.doPoolUpgrade(upgrade)
    reqs = wallet.preparePending()
    req, = client.submitReqs(*reqs)
    return upgrade, req


def ensureUpgradeSent(looper, trustee, trusteeWallet, upgradeData):
    upgrade, req = sendUpgrade(trustee, trusteeWallet, upgradeData)
    waitForSufficientRepliesForRequests(looper, trustee, requests=[req])

    def check():
        assert trusteeWallet.getPoolUpgrade(upgrade.key).seqNo

    timeout = plenumWaits.expectedReqAckQuorumTime()
    looper.run(eventually(check, retryWait=1, timeout=timeout))
    return upgrade


def checkUpgradeScheduled(nodes, version):
    for node in nodes:
        assert len(node.upgrader.aqStash) > 0
        assert node.upgrader.scheduledUpgrade
        assert node.upgrader.scheduledUpgrade[0] == version


def checkNoUpgradeScheduled(nodes):
    for node in nodes:
        assert len(node.upgrader.aqStash) == 0
        assert node.upgrader.scheduledUpgrade is None


def codeVersion():
    return Upgrader.getVersion()


def bumpVersion(v):
    parts = v.split('.')
    return '.'.join(parts[:-1] + [str(int(parts[-1]) + 1)])


def bumpedVersion():
    v = codeVersion()
    return bumpVersion(v)


class NodeControlToolExecutor:
    def __init__(self, transform = lambda tool: None):
        self.tool = NodeControlTool()
        transform(self.tool)
        self.p = multiprocessing.Process(target = self.tool.start)
        self.p.start()
    
    def stop(self):
        self.p.terminate()
        self.tool.server.close()


def composeUpgradeMessage(version):
    return (json.dumps({"version": version})).encode()


def sendUpgradeMessage(version):
    sock = socket.create_connection((config.controlServiceHost, config.controlServicePort))
    sock.sendall(composeUpgradeMessage(version))
    sock.close()


def nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout):
    ret = type("", (), {})()
    ret.returncode = 0
    ret.stdout = stdout
    tool.base_dir = tdir
    tool.sovrin_dir = os.path.join(tool.base_dir, '.sovrin')
    tool.tmp_dir = os.path.join(tool.base_dir, '.sovrin_tmp')
    if not os.path.exists(tool.sovrin_dir):
        os.mkdir(tool.sovrin_dir)
    if not os.path.exists(tool.tmp_dir):
        os.mkdir(tool.tmp_dir)
    monkeypatch.setattr(subprocess, 'run', lambda *x, **y: ret)
    monkeypatch.setattr(tool, '_migrate', lambda *x: None)


def get_valid_code_hash():
    return randomString(64)
