from datetime import datetime, timedelta

import dateutil
import pytest

from indy_common.config_helper import NodeConfigHelper
from indy_node.test.conftest import sdk_node_theta_added
from indy_node.test.upgrade.helper import sdk_ensure_upgrade_sent
from plenum.common.constants import TXN_TYPE, DATA, VERSION, CURRENT_PROTOCOL_VERSION

from indy_common.authorize.auth_actions import ADD_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_common.authorize.auth_map import add_new_identity_owner, txn_author_agreement, \
    txn_author_agreement_aml
from indy_common.constants import NODE_UPGRADE, ACTION, COMPLETE, AUTH_RULE, START
from indy_node.test.helper import sdk_send_and_check_auth_rule_request, TestNode
from plenum.common.request import Request
from plenum.common.types import f
from plenum.test.node_catchup.helper import waitNodeDataEquality

from plenum.test.helper import assertEquality
from stp_core.loop.eventually import eventually


@pytest.fixture(scope="module")
def tconf(tconf):
    old_version_matching = tconf.INDY_VERSION_MATCHING
    tconf.INDY_VERSION_MATCHING = {"1.1.58": "1.9.1"}
    yield tconf
    tconf.INDY_VERSION_MATCHING = old_version_matching


@pytest.fixture(scope='module')
def auth_keys(nodeSet, tconf):
    return [add_new_identity_owner, txn_author_agreement, txn_author_agreement_aml]


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
    looper.run(eventually(lambda: assertEquality(nodes[0].master_last_ordered_3PC[1],
                                                 last_ordered + count)))


def send_auth_rule(looper,
                   sdk_pool_handle,
                   sdk_wallet_trustee,
                   original_action):
    sdk_send_and_check_auth_rule_request(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         auth_action=ADD_PREFIX, auth_type=original_action.txn_type,
                                         field=original_action.field, new_value=original_action.value,
                                         old_value=None, constraint=AuthConstraint(role="*",
                                                                                   sig_count=1).as_dict)


def test_state_recovering_for_auth_rule(nodeSet, looper, sdk_pool_handle, sdk_wallet_steward,
                                        sdk_wallet_trustee,
                                        tdir, tconf,
                                        allPluginsPath,
                                        valid_upgrade,
                                        auth_keys,
                                        monkeypatch):
    version1 = "1.1.58"
    version2 = "1.1.88"

    # send POOL_UPGRADE to write in a ledger
    sdk_ensure_upgrade_sent(looper, sdk_pool_handle, sdk_wallet_trustee,
                            valid_upgrade)
    send_node_upgrades(nodeSet, version1, looper, count=1)
    send_auth_rule(looper,
                   sdk_pool_handle,
                   sdk_wallet_trustee,
                   auth_keys[0])
    send_node_upgrades(nodeSet, version1, looper)
    for n in nodeSet:
        handler = n.write_manager.request_handlers.get(AUTH_RULE)[0]
        handler_for_1_9_1 = n.write_manager._request_handlers_with_version.get((AUTH_RULE, "1.9.1"))[0]
        monkeypatch.setattr(handler, '_update_auth_constraint',
                            handler_for_1_9_1._update_auth_constraint)
    send_auth_rule(looper,
                   sdk_pool_handle,
                   sdk_wallet_trustee,
                   auth_keys[1])
    monkeypatch.undo()
    send_node_upgrades(nodeSet, version2, looper)
    send_auth_rule(looper,
                   sdk_pool_handle,
                   sdk_wallet_trustee,
                   auth_keys[2])

    new_steward_wallet, new_node = sdk_node_theta_added(looper,
                                                        nodeSet,
                                                        tdir,
                                                        tconf,
                                                        sdk_pool_handle,
                                                        sdk_wallet_trustee,
                                                        allPluginsPath,
                                                        node_config_helper_class=NodeConfigHelper,
                                                        testNodeClass=TestNode)
    waitNodeDataEquality(looper, new_node, *nodeSet[:-1], exclude_from_check=['check_last_ordered_3pc_backup'])
