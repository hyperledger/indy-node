import pytest

from indy_common.authorize.auth_actions import ADD_PREFIX, AuthActionAdd
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_common.constants import ROLE
from indy_node.test.auth_rule.test_auth_rule_transaction import sdk_send_and_check_auth_rule_request
from indy_node.test.auth_rule.test_check_rule_for_add_action_changing import create_verkey_did
from plenum.common.constants import STEWARD, NYM, STEWARD_STRING
from plenum.common.exceptions import RequestRejectedException
from plenum.common.startable import Mode
from plenum.test import waits
from plenum.test.delayers import cDelay, pDelay
from plenum.test.helper import assertExp
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from plenum.test.stasher import delay_rules_without_processing
from plenum.test.test_node import ensureElectionsDone
from plenum.test.view_change.helper import ensure_view_change
from stp_core.loop.eventually import eventually


def test_revert_auth_rule_changing(looper,
                                   txnPoolNodeSet,
                                   sdk_wallet_trustee,
                                   sdk_wallet_steward,
                                   sdk_pool_handle):
    node_stashers = [n.nodeIbStasher for n in txnPoolNodeSet]
    wh, _ = sdk_wallet_trustee
    new_steward_did, new_steward_verkey = create_verkey_did(looper, wh)
    new_steward_did2, new_steward_verkey2 = create_verkey_did(looper, wh)
    """We try to change rule for adding new steward. For this case we """
    changed_constraint = AuthConstraint(role=STEWARD,
                                        sig_count=1)
    action = AuthActionAdd(txn_type=NYM,
                           field=ROLE,
                           value=STEWARD)
    with delay_rules_without_processing(node_stashers, pDelay(), cDelay()):
        sdk_send_and_check_auth_rule_request(looper, sdk_wallet_trustee,
                                             sdk_pool_handle, auth_action=ADD_PREFIX,
                                             auth_type=action.txn_type,
                                             field=action.field,
                                             new_value=action.value,
                                             old_value=None,
                                             constraint=changed_constraint.as_dict,
                                             no_wait=True)
        looper.runFor(waits.expectedPrePrepareTime(len(txnPoolNodeSet)))
        """
        Try to add new steward by already existed trustee.
        Validation should raise exception because we change uncommitted state
        by adding new rule, that "Only steward can add new steward"
        """
        with pytest.raises(RequestRejectedException, match="TRUSTEE can not do this action"):
            sdk_add_new_nym(looper,
                            sdk_pool_handle,
                            sdk_wallet_trustee,
                            'newSteward1',
                            STEWARD_STRING,
                            dest=new_steward_did, verkey=new_steward_verkey)
        looper.runFor(waits.expectedPrePrepareTime(len(txnPoolNodeSet)))
        """
        Catchup should revert config_state and discard rule changing
        """
        for n in txnPoolNodeSet:
            n.start_catchup()
        for n in txnPoolNodeSet:
            looper.run(eventually(lambda: assertExp(n.mode == Mode.participating)))

    """
    Try to create new steward by steward
    We can not do this, because AUTH_RULE txn was reverted
    """
    with pytest.raises(RequestRejectedException, match="STEWARD can not do this action"):
        sdk_add_new_nym(looper,
                        sdk_pool_handle,
                        sdk_wallet_steward,
                        'newSteward2',
                        STEWARD_STRING,
                        dest=new_steward_did2, verkey=new_steward_verkey2)
    # """But with rules before sending AUTH_RULE txn (by default) we can add new steward"""
    # sdk_add_new_nym(looper,
    #                 sdk_pool_handle,
    #                 sdk_wallet_trustee,
    #                 'newSteward3',
    #                 STEWARD_STRING,
    #                 dest=new_steward_did2, verkey=new_steward_verkey2)