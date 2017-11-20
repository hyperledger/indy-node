from plenum.common.util import randomString
from stp_core.loop.eventually import eventually
from plenum.test.helper import waitForSufficientRepliesForRequests
from plenum.test import waits as plenumWaits
from plenum.common.types import f
from plenum.common.constants import TXN_TYPE, DATA, VERSION
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
from stp_core.common.log import getlogger

config = getConfig()
logger = getlogger()

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
        logger.debug("NCTProcess was started with pid: {}". format(self.p.pid))

    def stop(self):
        logger.debug("Send stop to NCTProcess with pid: {}". format(self.p.pid))
        self.tool.server.close()
        self.p.terminate()
        # check that process with NetControlTool.start function really stop.
        # process.terminate() just send SIGTERM and is not guarantee that process stops
        while self.p.is_alive():
            logger.debug("NCTProcess still alive, with pid: {}". format(self.p.pid))
            # while process is still alive, join with main process and wait
            self.p.join(3)
        logger.debug("NCTProcess must be stopped, with pid: {}". format(self.p.pid))



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


def check_node_sent_acknowledges_upgrade(
        looper, node_set, node_ids, allowed_actions: List, ledger_size, expected_version):
    '''
    Check that each node has sent NODE_UPGRADE txn with the specified actions
    '''
    check = functools.partial(
        check_ledger_after_upgrade,
        node_set,
        allowed_actions,
        ledger_size,
        expected_version,
        node_ids=node_ids)

    timeout = plenumWaits.expectedTransactionExecutionTime(len(node_set))
    looper.run(
        eventually(
            check,
            retryWait=1,
            timeout=timeout))


def emulate_restart_pool_for_upgrade(nodes):
    for node in nodes:
        node.upgrader = node.getUpgrader()
        node.acknowledge_upgrade()


def emulate_view_change_pool_for_upgrade(nodes):
    for node in nodes:
        node.upgrader.processLedger()
        node.acknowledge_upgrade()


def check_node_do_not_sent_acknowledges_upgrade(
        looper, node_set, node_ids, allowed_actions: List, ledger_size, expected_version):
    '''
    Check that each node has sent NODE_UPGRADE txn with the specified actions
    '''
    looper.runFor(5)
    check_ledger_after_upgrade(node_set, allowed_actions,
                               ledger_size, expected_version,
                               node_ids=node_ids)

def check_ledger_after_upgrade(
        node_set,
        allowed_actions,
        ledger_size,
        expected_version,
        allowed_txn_types=[NODE_UPGRADE],
        node_ids=None):
    versions = set()
    for node in node_set:
        # print(len(node.configLedger))
        assert len(node.configLedger) == ledger_size
        ids = set()
        for _, txn in node.configLedger.getAllTxn():
            type = txn[TXN_TYPE]
            assert type in allowed_txn_types
            data = txn
            if type == NODE_UPGRADE:
                data = txn[DATA]

            assert data[ACTION]
            assert data[ACTION] in allowed_actions
            ids.add(txn[f.IDENTIFIER.nm])

            assert data[VERSION]
            versions.add(data[VERSION])
        ids.add(node.id)

        if node_ids:
            assert ids == set(node_ids)
    assert len(versions) == 1
    assert list(versions)[0] == expected_version


def check_no_loop(nodeSet, event):
    for node in nodeSet:
        # mimicking upgrade start
        node.upgrader._upgradeLog.appendStarted(datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc()),
                                                node.upgrader.scheduledUpgrade[0],
                                                node.upgrader.scheduledUpgrade[2])
        node.notify_upgrade_start()
        # mimicking upgrader's initialization after restart
        node.upgrader.process_upgrade_log_for_first_run()

        node.upgrader.scheduledUpgrade = None
        assert node.upgrader._upgradeLog.lastEvent[1] == event
        # mimicking node's catchup after restart
        node.postConfigLedgerCaughtUp()
        assert node.upgrader.scheduledUpgrade is None
        assert node.upgrader._upgradeLog.lastEvent[1] == event
