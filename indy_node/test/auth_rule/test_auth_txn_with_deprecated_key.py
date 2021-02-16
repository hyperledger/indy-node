import shutil
from contextlib import contextmanager

import pytest

from indy_common.config_helper import NodeConfigHelper
from indy_node.test.helper import TestNode
from plenum.test.node_catchup.helper import ensure_all_nodes_have_same_data
from plenum.test.test_node import ensureElectionsDone, ensure_node_disconnected, checkNodesConnected
from indy_node.test.auth_rule.helper import sdk_send_and_check_auth_rule_request, sdk_send_and_check_get_auth_rule_request
from indy_common.authorize.auth_actions import ADD_PREFIX, AuthActionAdd
from indy_common.authorize.auth_constraints import AuthConstraint, ROLE
from indy_common.constants import CONSTRAINT, AUTH_TYPE, CONFIG_LEDGER_ID, NYM
from indy_common.authorize.auth_map import one_trustee_constraint
from plenum.common.constants import STEWARD, DATA
from plenum.common.exceptions import RequestNackedException


@contextmanager
def extend_auth_map(nodes, key, constraint):
    """
    Context manager to add a new auth rule to the auth map and remove it on exit.

    :param nodes: nodes list which auth maps should be changed
    :param key: str gotten from AuthActionAdd(...).get_action_id()
    :param constraint: AuthConstraint
    """
    for node in nodes:
        node.write_req_validator.auth_map[key] = constraint
    yield
    for node in nodes:
        node.write_req_validator.auth_map.pop(key, None)


def test_auth_txn_with_deprecated_key(tconf, tdir, allPluginsPath,
                                      txnPoolNodeSet,
                   looper,
                   sdk_wallet_trustee,
                   sdk_pool_handle):
    """
    Add to the auth_map a fake rule
    Send AUTH_RULE txn to change this fake rule (and set the fake key to the config state)
    Send GET_AUTH_RULE txn and check that the fake rule was changed
    Remove the fake auth rule from the map
    Check that we can't get the fake auth rule
    Restart the last node with its state regeneration
    Check that nodes data is equal after changing the existing auth rule (restarted node regenerate config state)
    """

    fake_txn_type = "100002"
    fake_key = AuthActionAdd(txn_type=fake_txn_type,
                                field="*",
                                value="*").get_action_id()
    fake_constraint = one_trustee_constraint
    new_auth_constraint = AuthConstraint(role=STEWARD, sig_count=1, need_to_be_owner=False).as_dict

    # Add to the auth_map a fake rule
    with extend_auth_map(txnPoolNodeSet,
                         fake_key,
                         fake_constraint):
        # Send AUTH_RULE txn to change this fake rule (and set the fake key to the config state)
        sdk_send_and_check_auth_rule_request(looper,
                                             sdk_pool_handle,
                                             sdk_wallet_trustee,
                                             auth_action=ADD_PREFIX,
                                             auth_type=fake_txn_type,
                                             field='*',
                                             new_value='*',
                                             constraint=new_auth_constraint)
        # Send GET_AUTH_RULE txn and check that the fake rule was changed
        result = sdk_send_and_check_get_auth_rule_request(
            looper,
            sdk_pool_handle,
            sdk_wallet_trustee,
            auth_type=fake_txn_type,
            auth_action=ADD_PREFIX,
            field="*",
            new_value="*"
        )[0][1]["result"][DATA][0]
        assert result[AUTH_TYPE] == fake_txn_type
        assert result[CONSTRAINT] == new_auth_constraint

    # Remove the fake auth rule from the map
    # Check that we can't get the fake auth rule
    with pytest.raises(RequestNackedException, match="not found in authorization map"):
        sdk_send_and_check_auth_rule_request(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         auth_action=ADD_PREFIX,
                                         auth_type=fake_txn_type,
                                         field='*',
                                         new_value='*',
                                         constraint=AuthConstraint(role=STEWARD, sig_count=2,
                                                                   need_to_be_owner=False).as_dict)

    resp = sdk_send_and_check_get_auth_rule_request(looper,
                                                    sdk_pool_handle,
                                                    sdk_wallet_trustee)

    assert all(rule[AUTH_TYPE] != fake_txn_type for rule in resp[0][1]["result"][DATA])

    with pytest.raises(RequestNackedException, match="not found in authorization map"):
        sdk_send_and_check_get_auth_rule_request(
            looper,
            sdk_pool_handle,
            sdk_wallet_trustee,
            auth_type=fake_txn_type,
            auth_action=ADD_PREFIX,
            field="*",
            new_value="*"
        )
    # Restart the last node with its state regeneration
    ensure_all_nodes_have_same_data(looper, txnPoolNodeSet)

    node_to_stop = txnPoolNodeSet[-1]
    node_state = node_to_stop.states[CONFIG_LEDGER_ID]
    assert not node_state.isEmpty
    state_db_path = node_state._kv.db_path
    node_to_stop.cleanupOnStopping = False
    node_to_stop.stop()
    looper.removeProdable(node_to_stop)
    ensure_node_disconnected(looper, node_to_stop, txnPoolNodeSet[:-1])

    shutil.rmtree(state_db_path)

    config_helper = NodeConfigHelper(node_to_stop.name, tconf, chroot=tdir)
    restarted_node = TestNode(
        node_to_stop.name,
        config_helper=config_helper,
        config=tconf,
        pluginPaths=allPluginsPath,
        ha=node_to_stop.nodestack.ha,
        cliha=node_to_stop.clientstack.ha)
    looper.add(restarted_node)
    txnPoolNodeSet[-1] = restarted_node

    # Check that nodes data is equal (restarted node regenerate config state)
    looper.run(checkNodesConnected(txnPoolNodeSet))
    ensureElectionsDone(looper, txnPoolNodeSet, customTimeout=30)
    sdk_send_and_check_auth_rule_request(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         auth_action=ADD_PREFIX,
                                         auth_type=NYM,
                                         field=ROLE,
                                         new_value=STEWARD,
                                         constraint=AuthConstraint(role=STEWARD, sig_count=2,
                                                                   need_to_be_owner=False).as_dict)
    ensure_all_nodes_have_same_data(looper, txnPoolNodeSet, custom_timeout=20)

