from indy_common.authorize.auth_actions import ADD_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_node.test.auth_rule.helper import create_verkey_did, sdk_send_and_check_auth_rule_request
from plenum.common.constants import STEWARD, NYM, ROLE, STEWARD_STRING
from plenum.test import waits
from plenum.test.delayers import cDelay
from plenum.test.helper import sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from plenum.test.stasher import delay_rules


def test_use_modified_rules_from_uncommitted(looper,
                                             txnPoolNodeSet,
                                             sdk_wallet_trustee,
                                             sdk_wallet_steward,
                                             sdk_pool_handle):
    node_stashers = [n.nodeIbStasher for n in txnPoolNodeSet]
    wh, _ = sdk_wallet_trustee
    new_steward_did, new_steward_verkey = create_verkey_did(looper, wh)
    changed_constraint = AuthConstraint(role=STEWARD,
                                        sig_count=1)
    with delay_rules(node_stashers, cDelay()):
        r_auth = sdk_send_and_check_auth_rule_request(looper, sdk_pool_handle, sdk_wallet_trustee,
                                                      auth_action=ADD_PREFIX,
                                                      auth_type=NYM, field=ROLE, new_value=STEWARD, old_value=None,
                                                      constraint=changed_constraint.as_dict, no_wait=True)
        looper.runFor(waits.expectedPrePrepareTime(len(txnPoolNodeSet)))
        r_add_steward = sdk_add_new_nym(looper,
                                        sdk_pool_handle,
                                        sdk_wallet_steward,
                                        'newSteward2',
                                        STEWARD_STRING,
                                        dest=new_steward_did, verkey=new_steward_verkey,
                                        no_wait=True)

    sdk_get_and_check_replies(looper, [r_auth])
    sdk_get_and_check_replies(looper, [r_add_steward])
