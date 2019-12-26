import pytest
from indy import did

from indy_common.authorize.auth_actions import AuthActionEdit, EDIT_PREFIX, ADD_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_common.authorize.auth_map import promote_node as promote_action
from indy_common.constants import ENDORSER_STRING, NODE, ENDORSER
from indy_node.test.auth_rule.helper import sdk_send_and_check_auth_rule_request, get_pool_validator_count
from plenum.test.pool_transactions.helper import sdk_add_new_nym, demote_node, promote_node


def test_node_txn_promote_by_endorser(txnPoolNodeSet,
                                     sdk_pool_handle,
                                     sdk_wallet_trustee,
                                     looper,
                                     sdk_wallet_handle):

    validators_before = get_pool_validator_count(txnPoolNodeSet)

    new_end_did, new_end_verkey = looper.loop.run_until_complete(
        did.create_and_store_my_did(sdk_wallet_trustee[0], "{}"))

    # Step 1. Demote node using default auth rule
    demote_node(looper, sdk_wallet_trustee, sdk_pool_handle, txnPoolNodeSet[-1])

    # Check, that node was demoted
    assert validators_before - get_pool_validator_count(txnPoolNodeSet[:-1]) == 1

    # Step 2. Add new Endorser
    sdk_add_new_nym(looper, sdk_pool_handle,
                    sdk_wallet_trustee,
                    'newEndorser',
                    ENDORSER_STRING,
                    verkey=new_end_verkey, dest=new_end_did)

    new_constraint = AuthConstraint(ENDORSER, 1)

    # Step 3. Change auth rule, to allowing endorser promote node back
    sdk_send_and_check_auth_rule_request(looper, sdk_pool_handle, sdk_wallet_trustee,
                                         auth_action=EDIT_PREFIX,
                                         auth_type=promote_action.txn_type,
                                         field=promote_action.field,
                                         new_value=promote_action.new_value,
                                         old_value=promote_action.old_value,
                                         constraint=new_constraint.as_dict)

    # Step 4. Promote node back, using new Endorser
    promote_node(looper, (sdk_wallet_handle, new_end_did), sdk_pool_handle, txnPoolNodeSet[-1])

    # Check, that all other nodes return previous demoted node back
    assert validators_before == get_pool_validator_count(txnPoolNodeSet[:-1])
