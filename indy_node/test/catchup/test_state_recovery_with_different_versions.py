import shutil
from datetime import datetime, timedelta

import dateutil
import pytest

from indy_node.test.fees.helper import sdk_set_fees
from stp_core.ratchet import Ratchet

from indy_common.config_helper import NodeConfigHelper
from indy_node.test.upgrade.helper import sdk_ensure_upgrade_sent
from plenum.common.constants import TXN_TYPE, DATA, VERSION, CURRENT_PROTOCOL_VERSION
from indy_common.constants import NODE_UPGRADE, ACTION, COMPLETE, AUTH_RULE, START, SET_FEES
from indy_node.test.helper import sdk_send_and_check_auth_rule_request, TestNode
from plenum.common.request import Request
from plenum.common.types import f
from plenum.test.node_catchup.helper import waitNodeDataEquality

from plenum.test.helper import assertEquality
from plenum.test.test_node import checkNodesConnected, ensure_node_disconnected
from stp_core.loop.eventually import eventually


@pytest.fixture(scope="module")
def tconf(tconf):
    old_version_matching = tconf.INDY_VERSION_MATCHING
    tconf.INDY_VERSION_MATCHING = {"1.1.24": "0.9.3"}
    yield tconf
    tconf.INDY_VERSION_MATCHING = old_version_matching


@pytest.fixture(scope='module')
def valid_upgrade(nodeSet, tconf):
    schedule = {}
    unow = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    startAt = unow + timedelta(seconds=30000000)
    acceptableDiff = tconf.MinSepBetweenNodeUpgrades + 1
    for n in nodeSet[0].poolManager.nodeIds:
        schedule[n] = datetime.isoformat(startAt)
        startAt = startAt + timedelta(seconds=acceptableDiff + 3)

    return dict(name='upgrade', version="10000.10.10",
                action=START, schedule=schedule, timeout=1,
                package=None,
                sha256='db34a72a90d026dae49c3b3f0436c8d3963476c77468ad955845a1ccf7b03f55')


def send_node_upgrades(nodes, version, looper, count=None):
    if count is None:
        count = len(nodes)
    last_ordered = nodes[0].master_last_ordered_3PC[1]
    for node in nodes[:count]:
        op = {
            TXN_TYPE: NODE_UPGRADE,
            DATA: {
                ACTION: COMPLETE,
                VERSION: version
            }
        }
        op[f.SIG.nm] = node.wallet.signMsg(op[DATA])

        request = node.wallet.signRequest(
            Request(operation=op, protocolVersion=CURRENT_PROTOCOL_VERSION))

        node.startedProcessingReq(request.key, node.nodestack.name)
        node.send(request)
        looper.run(eventually(lambda: assertEquality(node.master_last_ordered_3PC[1],
                                                         last_ordered + 1)))
        last_ordered += 1


def test_state_recovery_with_fees(looper, tconf, tdir,
                                  sdk_pool_handle,
                                  sdk_wallet_trustee,
                                  allPluginsPath,
                                  do_post_node_creation,
                                  nodeSet,
                                  valid_upgrade,
                                  monkeypatch):
    version1 = "1.1.24"
    version2 = "1.1.88"
    node_set = nodeSet
    # send POOL_UPGRADE to write in a ledger
    last_ordered = node_set[0].master_last_ordered_3PC[1]
    sdk_ensure_upgrade_sent(looper, sdk_pool_handle, sdk_wallet_trustee,
                            valid_upgrade)
    looper.run(eventually(lambda: assertEquality(node_set[0].master_last_ordered_3PC[1],
                                                     last_ordered + 1)))

    send_node_upgrades(node_set, version1, looper)
    for n in node_set:
        handler = n.write_manager.request_handlers.get(SET_FEES)[0]
        handler_for_0_9_3 = n.write_manager._request_handlers_with_version.get((SET_FEES, "0.9.3"))[0]
        monkeypatch.setattr(handler, 'update_state',
                            handler_for_0_9_3.update_state)
        monkeypatch.setattr(handler, 'static_validation', lambda _: _)
        monkeypatch.setattr(handler, 'additional_dynamic_validation', lambda a, b: 0)
    sdk_set_fees(looper, sdk_pool_handle, sdk_wallet_trustee, {"A": 2})
    send_node_upgrades(node_set, version2, looper)
    for n in node_set:
        handler = n.write_manager.request_handlers.get(SET_FEES)[0]
        monkeypatch.delattr(handler, 'update_state')
    sdk_set_fees(looper, sdk_pool_handle, sdk_wallet_trustee, {"B": 2})
    monkeypatch.undo()
    node_to_stop = node_set[-1]
    state_db_pathes = [state._kv.db_path
                       for state in node_to_stop.states.values()]
    node_to_stop.cleanupOnStopping = False
    node_to_stop.stop()
    looper.removeProdable(node_to_stop)
    ensure_node_disconnected(looper, node_to_stop, node_set[:-1])

    for path in state_db_pathes:
        shutil.rmtree(path)
    config_helper = NodeConfigHelper(node_to_stop.name, tconf, chroot=tdir)
    restarted_node = TestNode(
        node_to_stop.name,
        config_helper=config_helper,
        config=tconf,
        pluginPaths=allPluginsPath,
        ha=node_to_stop.nodestack.ha,
        cliha=node_to_stop.clientstack.ha)
    do_post_node_creation(restarted_node)

    looper.add(restarted_node)
    node_set[-1] = restarted_node

    looper.run(checkNodesConnected(node_set))
    waitNodeDataEquality(looper, restarted_node, *node_set[:-1], exclude_from_check=['check_last_ordered_3pc_backup'])
