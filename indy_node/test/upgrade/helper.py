from plenum.common.util import randomString
from stp_core.loop.eventually import eventually
from plenum.test.helper import waitForSufficientRepliesForRequests
from plenum.test import waits as plenumWaits
from plenum.common.types import f
from plenum.common.constants import TXN_TYPE, DATA
from indy_common.constants import NODE_UPGRADE, ACTION
from indy_client.client.wallet.upgrade import Upgrade
from indy_node.server.upgrader import Upgrader
from indy_node.server.upgrade_log import UpgradeLog
from indy_node.utils.node_control_tool import NodeControlTool
from indy_common.config_util import getConfig
from datetime import datetime
from typing import List, Tuple
import dateutil.tz
import subprocess
import os
import multiprocessing
import socket
import json
import functools


config = getConfig()


def sendUpgrade(client, wallet, upgradeData):
    upgrade = Upgrade(**upgradeData, trustee=wallet.defaultId)
    wallet.doPoolUpgrade(upgrade)
    reqs = wallet.preparePending()
    req = client.submitReqs(*reqs)[0][0]
    return upgrade, req


def ensureUpgradeSent(looper, trustee, trusteeWallet, upgradeData):
    upgrade, req = sendUpgrade(trustee, trusteeWallet, upgradeData)
    waitForSufficientRepliesForRequests(looper, trustee, requests=[req])

    def check():
        assert trusteeWallet.getPoolUpgrade(upgrade.key).seqNo

    timeout = plenumWaits.expectedReqAckQuorumTime()
    looper.run(eventually(check, retryWait=1, timeout=timeout))
    return upgrade


def checkUpgradeScheduled(nodes, version, schedule=None):
    for node in nodes:
        assert len(node.upgrader.aqStash) == 1
        assert node.upgrader.scheduledUpgrade
        assert node.upgrader.scheduledUpgrade[0] == version
        if schedule:
            assert node.upgrader.scheduledUpgrade[1] == \
                   dateutil.parser.parse(schedule[node.id])


def checkNoUpgradeScheduled(nodes):
    for node in nodes:
        assert len(node.upgrader.aqStash) == 0
        assert node.upgrader.scheduledUpgrade is None


def codeVersion():
    return Upgrader.getVersion()


def bumpVersion(v):
    parts = v.split('.')
    return '.'.join(parts[:-1] + [str(int(parts[-1]) + 1)])


def lowerVersion(v):
    parts = v.split('.')
    for i in reversed(range(len(parts))):
        if int(parts[i]) > 0:
            parts[i] = str(int(parts[i]) - 1)
            break
    else:
        raise ValueError('Version {} cannot be lowered'.format(v))
    return '.'.join(parts)


def bumpedVersion():
    v = codeVersion()
    return bumpVersion(v)


def loweredVersion():
    v = codeVersion()
    return lowerVersion(v)


class NodeControlToolExecutor:
    def __init__(self, backup_dir, backup_target, transform=lambda tool: None):
        self.tool = NodeControlTool(backup_dir=backup_dir, backup_target=backup_target)
        transform(self.tool)
        self.p = multiprocessing.Process(target=self.tool.start)
        self.p.start()

    def stop(self):
        self.p.terminate()
        self.tool.server.close()


def composeUpgradeMessage(version):
    return (json.dumps({"version": version})).encode()


def sendUpgradeMessage(version):
    sock = socket.create_connection(
        (config.controlServiceHost, config.controlServicePort))
    sock.sendall(composeUpgradeMessage(version))
    sock.close()


def nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout):
    ret = type("", (), {})()
    ret.returncode = 0
    ret.stdout = stdout
    tool.base_dir = tdir
    tool.indy_dir = os.path.join(tool.base_dir, '.indy')
    tool.tmp_dir = os.path.join(tool.base_dir, '.indy_tmp')
    if not os.path.exists(tool.indy_dir):
        os.mkdir(tool.indy_dir)
    if not os.path.exists(tool.tmp_dir):
        os.mkdir(tool.tmp_dir)
    monkeypatch.setattr(subprocess, 'run', lambda *x, **y: ret)
    monkeypatch.setattr(tool, '_migrate', lambda *x: None)


def get_valid_code_hash():
    return randomString(64)


def populate_log_with_upgrade_events(
        tdir_with_pool_txns, pool_txn_node_names, tconf, version: Tuple[str, str, str]):
    for nm in pool_txn_node_names:
        path = os.path.join(tdir_with_pool_txns, tconf.nodeDataDir, nm)
        os.makedirs(path)
        log = UpgradeLog(os.path.join(path, tconf.upgradeLogFile))
        when = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
        log.appendScheduled(when, version, randomString(10))
        log.appendStarted(when, version, randomString(10))


def check_node_set_acknowledges_upgrade(
        looper, node_set, node_ids, allowed_actions: List, version: Tuple[str, str, str]):
    check = functools.partial(
        check_ledger_after_upgrade,
        node_set,
        allowed_actions,
        node_ids=node_ids)

    for node in node_set:
        node.upgrader.scheduledUpgrade = (version,
                                          datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc()),
                                          randomString(10))
        node.notify_upgrade_start()
        node.upgrader.scheduledUpgrade = None

    timeout = plenumWaits.expectedTransactionExecutionTime(len(node_set))
    looper.run(eventually(functools.partial(
        check, ledger_size=len(node_set)), retryWait=1, timeout=timeout))

    for node in node_set:
        node.acknowledge_upgrade()

    looper.run(
        eventually(
            functools.partial(
                check,
                ledger_size=2 *
                len(node_set)),
            retryWait=1,
            timeout=timeout))


def check_ledger_after_upgrade(
        node_set,
        allowed_actions,
        ledger_size,
        node_ids=None,
        allowed_txn_types=[NODE_UPGRADE]):
    for node in node_set:
        print(len(node.configLedger))
        assert len(node.configLedger) == ledger_size
        ids = set()
        for _, txn in node.configLedger.getAllTxn():
            type = txn[TXN_TYPE]
            assert type in allowed_txn_types
            data = txn
            if type == NODE_UPGRADE:
                data = txn[DATA]
            assert data[ACTION] in allowed_actions
            ids.add(txn[f.IDENTIFIER.nm])
        ids.add(node.id)

        if node_ids:
            assert ids == set(node_ids)


def check_no_loop(nodeSet, event):
    for node in nodeSet:
        # mimicking upgrade start
        node.upgrader._upgradeLog.appendStarted(datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc()),
                                                node.upgrader.scheduledUpgrade[0],
                                                node.upgrader.scheduledUpgrade[2])
        node.notify_upgrade_start()
        # mimicking upgrader's initialization after restart
        node.upgrader.check_upgrade_succeeded()
        node.upgrader.scheduledUpgrade = None
        assert node.upgrader._upgradeLog.lastEvent[1] == event
        # mimicking node's catchup after restart
        node.postConfigLedgerCaughtUp()
        assert node.upgrader.scheduledUpgrade is None
        assert node.upgrader._upgradeLog.lastEvent[1] == event
