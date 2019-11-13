from indy_common.authorize.auth_actions import ADD_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraintForbidden
from indy_common.authorize.auth_map import auth_map, add_new_identity_owner, txn_author_agreement
from indy_common.constants import NYM
from indy_node.test.helper import sdk_send_and_check_auth_rule_request
from plenum.test.node_catchup.helper import waitNodeDataEquality
from plenum.test.test_node import checkNodesConnected

from plenum.test.helper import assertEquality
from plenum.test.pool_transactions.helper import sdk_add_new_steward_and_node
from plenum.test.testing_utils import FakeSomething


def send_node_upgrades(nodes, version):
    for node in nodes:
        node._should_notify_about_upgrade = True
        node.upgrader.lastActionEventInfo.data.version = FakeSomething(full=version)
        node.acknowledge_upgrade()


def send_auth_rule1(looper,
                    sdk_pool_handle,
                    sdk_wallet_trustee):
    original_action = add_new_identity_owner
    sdk_send_and_check_auth_rule_request(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         auth_action=ADD_PREFIX, auth_type=original_action.txn_type,
                                         field=original_action.field, new_value=original_action.value,
                                         old_value=None, constraint=AuthConstraintForbidden().as_dict)


def send_auth_rule2(looper,
                    sdk_pool_handle,
                    sdk_wallet_trustee):
    original_action = txn_author_agreement
    sdk_send_and_check_auth_rule_request(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         auth_action=ADD_PREFIX, auth_type=original_action.txn_type,
                                         field=original_action.field, new_value=original_action.value,
                                         old_value=None, constraint=AuthConstraintForbidden().as_dict)


def test_node_detected_upgrade_done(nodeSet, looper, sdk_pool_handle, sdk_wallet_steward,
                                    sdk_wallet_trustee,
                                    tdir, tconf,
                                    all_plugins_path,
                                    monkeypatch):
    '''
    Test that each node checks Upgrade Log on startup (after Upgrade restart), and writes SUCCESS to it
    because the current version equals to the one in Upgrade log.
    Upgrade log already created START event (see fixture above emulating real upgrade)
    '''
    version1 = "1.9.1"
    version1 = "1.1.85"
    last_ordered = nodeSet[0].master_replica.last_ordered_3pc
    send_node_upgrades(nodeSet, version1)
    for n in nodeSet:
        monkeypatch.setattr(n, '_update_auth_constraint',
                            n._update_auth_constraint_for_1_9_1)
    send_auth_rule1(looper,
                    sdk_pool_handle,
                    sdk_wallet_trustee)
    monkeypatch.undo()
    send_auth_rule2(looper,
                    sdk_pool_handle,
                    sdk_wallet_trustee)

    _, new_node = sdk_add_new_steward_and_node(
        looper, sdk_pool_handle, sdk_wallet_steward,
        "new_steward", "Theta", tdir, tconf,
        allPluginsPath=all_plugins_path)
    nodeSet.append(new_node)
    looper.run(checkNodesConnected(nodeSet))
    waitNodeDataEquality(looper, new_node, *nodeSet[:-1], exclude_from_check=['check_last_ordered_3pc_backup'])
