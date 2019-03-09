import functools
import json
import multiprocessing
import os
import socket
import subprocess
from datetime import datetime
from typing import List, Tuple

import base58
import dateutil.tz
from plenum.bls.bls_crypto_factory import create_default_bls_crypto_factory
from plenum.test.node_catchup.helper import waitNodeDataEquality, ensure_all_nodes_have_same_data

from plenum.common.keygen_utils import init_bls_keys

from indy.ledger import build_pool_upgrade_request
from plenum.common.constants import DATA, VERSION, FORCE
from plenum.common.txn_util import get_type, get_payload_data, get_from
from plenum.common.util import randomString, hexToFriendly
from plenum.test import waits as plenumWaits
from plenum.test.helper import sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import sdk_sign_and_send_prepared_request, sdk_send_update_node, \
    sdk_pool_refresh, sdk_add_new_nym
from stp_core.common.log import getlogger
from stp_core.loop.eventually import eventually

from indy_common.constants import NODE_UPGRADE, ACTION, \
    UPGRADE_MESSAGE, MESSAGE_TYPE, APP_NAME
from indy_common.config import controlServiceHost, controlServicePort
import indy_node
from indy_node.server.upgrade_log import UpgradeLogData, UpgradeLog
from indy_node.server.upgrader import Upgrader
from indy_node.test.helper import TestNode
from indy_node.utils.node_control_tool import NodeControlTool
from indy_common.config_helper import NodeConfigHelper

logger = getlogger()


class TestNodeNoProtocolVersion(TestNode):
    def processNodeRequest(self, request, frm):
        if request.protocolVersion is not None:
            raise ValueError('Do not understand what protocolVersion is!!!')
        super().processNodeRequest(request, frm)


def sdk_send_upgrade(looper, sdk_pool_handle, sdk_wallet_trustee, upgrade_data):
    _, did = sdk_wallet_trustee
    req = get_req_from_update(looper, did, upgrade_data)
    return sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                              sdk_pool_handle, req)


def sdk_ensure_upgrade_sent(looper, sdk_pool_handle,
                            sdk_wallet_trustee, upgrade_data):
    req = sdk_send_upgrade(looper, sdk_pool_handle, sdk_wallet_trustee, upgrade_data)
    sdk_get_and_check_replies(looper, [req])


def get_req_from_update(looper, did, nup):
    req = looper.loop.run_until_complete(
        build_pool_upgrade_request(did, nup['name'], nup['version'], nup['action'], nup['sha256'],
                                   nup['timeout'],
                                   json.dumps(nup['schedule']) if 'schedule' in nup else None,
                                   nup['justification'] if 'justification' in nup else 'null',
                                   nup['reinstall'] if 'reinstall' in nup else None,
                                   nup[FORCE] if FORCE in nup else None,
                                   nup.get('package', None)))
    return req


def clear_aq_stash(nodes):
    for node in nodes:
        node.upgrader.aqStash.clear()


def checkUpgradeScheduled(nodes, version: str, schedule=None):
    for node in nodes:
        assert len(node.upgrader.aqStash) == 1
        assert node.upgrader.scheduledAction
        assert node.upgrader.scheduledAction.version.full == version
        if schedule:
            assert node.upgrader.scheduledAction.when == \
                   dateutil.parser.parse(schedule[node.id])


def checkNoUpgradeScheduled(nodes):
    for node in nodes:
        assert len(node.upgrader.aqStash) == 0
        assert node.upgrader.scheduledAction is None


def codeVersionInfo():
    return indy_node.__version_info__


def releaseVersion():
    return '.'.join(map(str, codeVersionInfo()[:3]))


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


def bumpedVersion(ver=None):
    return bumpVersion(ver or releaseVersion())


def loweredVersion():
    return lowerVersion(releaseVersion())


class NodeControlToolExecutor:
    def __init__(self, backup_dir, backup_target, transform=lambda tool: None):
        self.tool = NodeControlTool(backup_dir=backup_dir, backup_target=backup_target)
        transform(self.tool)
        self.p = multiprocessing.Process(target=self.tool.start)
        self.p.start()
        logger.debug("NCTProcess was started with pid: {}".format(self.p.pid))

    def stop(self):
        logger.debug("Send stop to NCTProcess with pid: {}".format(self.p.pid))
        self.tool.server.close()
        self.p.terminate()
        # check that process with NodeControlTool.start function really stop.
        # process.terminate() just send SIGTERM and is not guarantee that process stops
        if self.p.is_alive():
            logger.debug("NCTProcess still alive, with pid: {}".format(self.p.pid))
            # while process is still alive, join with main process and wait

            # FIXME: here was self.p.join(3), but since we've added (ok, Andrew Nikitin
            # has added) handler for SIGTERM here we wait for child process infinitely,
            # but for now we have no time to fix it in more elegant way as it is not a
            # real situation (Andrew said), so he has proposed this ugly hack.
            os.kill(self.p.pid, 9)
        logger.debug("NCTProcess must be stopped, with pid: {}".format(self.p.pid))


def composeUpgradeMessage(version, pkg_name: str = APP_NAME):
    return (json.dumps({"version": version, "pkg_name": pkg_name, MESSAGE_TYPE: UPGRADE_MESSAGE})).encode()


def sendUpgradeMessage(version, pkg_name: str = APP_NAME):
    sock = socket.create_connection(
        (controlServiceHost, controlServicePort))
    sock.sendall(composeUpgradeMessage(version, pkg_name=pkg_name))
    sock.close()


def nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, stdout):
    ret = type("", (), {})()
    ret.returncode = 0
    ret.stdout = stdout if isinstance(stdout, bytes) else stdout.encode()
    tool.base_dir = tdir
    tool.indy_dir = os.path.join(tool.base_dir, '.indy')
    tool.tmp_dir = os.path.join(tool.base_dir, '.indy_tmp')
    if not os.path.exists(tool.indy_dir):
        os.mkdir(tool.indy_dir)
    if not os.path.exists(tool.tmp_dir):
        os.mkdir(tool.tmp_dir)
    monkeypatch.setattr(subprocess, 'run', lambda *x, **y: ret)
    monkeypatch.setattr(tool, '_do_migration', lambda *x: None)


def get_valid_code_hash():
    return randomString(64)


def populate_log_with_upgrade_events(
        pool_txn_node_names, tdir, tconf, version: Tuple[str, str, str], pkg_name: str = APP_NAME):
    for nm in pool_txn_node_names:
        config_helper = NodeConfigHelper(nm, tconf, chroot=tdir)
        ledger_dir = config_helper.ledger_dir
        os.makedirs(ledger_dir)
        log = UpgradeLog(os.path.join(ledger_dir, tconf.upgradeLogFile))
        when = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
        ev_data = UpgradeLogData(when, version, randomString(10), pkg_name)
        log.append_scheduled(ev_data)
        log.append_started(ev_data)


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
        node.upgrader = node.init_upgrader()
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


def clear_config_ledger(node_set):
    for node in node_set:
        node.configLedger.reset_uncommitted()
        node.configLedger._transactionLog.reset()
        node.configLedger.tree.reset()


def check_ledger_after_upgrade(
        node_set,
        allowed_actions,
        ledger_size,
        expected_version,
        allowed_txn_types=[NODE_UPGRADE],
        node_ids=None):
    versions = set()
    for node in node_set:
        print(len(node.configLedger))
        assert len(node.configLedger) == ledger_size
        ids = set()
        for _, txn in node.configLedger.getAllTxn():
            type = get_type(txn)
            assert type in allowed_txn_types
            txn_data = get_payload_data(txn)
            data = txn_data
            if type == NODE_UPGRADE:
                data = txn_data[DATA]

            assert data[ACTION]
            assert data[ACTION] in allowed_actions
            ids.add(get_from(txn))

            assert data[VERSION]
            versions.add(data[VERSION])
        ids.add(node.id)

        if node_ids:
            assert ids == set(node_ids)
    assert len(versions) == 1
    assert list(versions)[0] == expected_version


def check_no_loop(nodeSet, ev_type, pkg_name: str = APP_NAME):
    for node in nodeSet:
        # mimicking upgrade start
        node.upgrader._actionLog.append_started(
            UpgradeLogData(
                datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc()),
                node.upgrader.scheduledAction.version,
                node.upgrader.scheduledAction.upgrade_id,
                pkg_name
            )
        )
        node.notify_upgrade_start()
        # mimicking upgrader's initialization after restart
        node.upgrader.process_action_log_for_first_run()

        node.upgrader.scheduledAction = None
        assert node.upgrader._actionLog.last_event.ev_type == ev_type
        # mimicking node's catchup after restart
        node.postConfigLedgerCaughtUp()
        assert node.upgrader.scheduledAction is None
        assert node.upgrader._actionLog.last_event.ev_type == ev_type


def sdk_change_bls_key(looper, txnPoolNodeSet,
                       node,
                       sdk_pool_handle,
                       sdk_wallet_steward,
                       add_wrong=False,
                       new_bls=None,
                       new_key_proof=None):
    if add_wrong:
        _, new_blspk, key_proof = create_default_bls_crypto_factory().generate_bls_keys()
    else:
        new_blspk, key_proof = init_bls_keys(node.keys_dir, node.name)
    key_in_txn = new_bls or new_blspk
    bls_key_proof = new_key_proof or key_proof
    node_dest = hexToFriendly(node.nodestack.verhex)
    sdk_send_update_node(looper, sdk_wallet_steward,
                         sdk_pool_handle,
                         node_dest, node.name,
                         None, None,
                         None, None,
                         bls_key=key_in_txn,
                         services=None,
                         key_proof=bls_key_proof)
    poolSetExceptOne = list(txnPoolNodeSet)
    poolSetExceptOne.remove(node)
    waitNodeDataEquality(looper, node, *poolSetExceptOne)
    sdk_pool_refresh(looper, sdk_pool_handle)
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_steward,
                    alias=randomString(5))
    ensure_all_nodes_have_same_data(looper, txnPoolNodeSet)
    return new_blspk


def count_action_log_entries(upg_log, func):
    ret = 0
    for upg_rec in upg_log:
        if func(upg_rec):
            ret += 1
    return ret


def count_action_log_package(upg_log, pkg_name):
    return count_action_log_entries(upg_log, lambda entry: entry.data.pkg_name == pkg_name)
