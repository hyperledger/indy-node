import pytest

from indy_common.authorize.auth_actions import ADD_PREFIX, AuthActionAdd
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_common.constants import ROLE
from indy_node.test.auth_rule.test_auth_rule_transaction import sdk_send_and_check_auth_rule_request
from indy_node.test.auth_rule.test_check_rule_for_add_action_changing import create_verkey_did
from plenum.common.constants import STEWARD, NYM, STEWARD_STRING, PREPARE, COMMIT, DOMAIN_LEDGER_ID, CONFIG_LEDGER_ID
from plenum.common.exceptions import RequestRejectedException
from plenum.common.startable import Mode
from plenum.test import waits
from plenum.test.delayers import cDelay, pDelay, msg_rep_delay
from plenum.test.helper import assertExp
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from plenum.test.stasher import delay_rules_without_processing
from plenum.test.view_change.helper import ensure_view_change_complete
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
    with delay_rules_without_processing(node_stashers, pDelay(), cDelay(),
                                        msg_rep_delay(types_to_delay=[PREPARE, COMMIT])):
        sdk_send_and_check_auth_rule_request(looper, sdk_pool_handle, sdk_wallet_trustee,
                                             auth_action=ADD_PREFIX,
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
        with pytest.raises(RequestRejectedException, match="Not enough STEWARD signatures"):
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
        # clear all request queues to not re-send the AuthRule txns again
        for n in txnPoolNodeSet:
            n.requests.clear()
            for r in n.replicas.values():
                r._ordering_service.requestQueues[DOMAIN_LEDGER_ID].clear()
                r._ordering_service.requestQueues[CONFIG_LEDGER_ID].clear()
        looper.run(
            eventually(lambda nodes: assertExp(all([n.mode == Mode.participating for n in nodes])), txnPoolNodeSet))

    # do view change to not send PrePrepares with the same ppSeqNo and viewNo
    ensure_view_change_complete(looper, txnPoolNodeSet)

    """
    Try to create new steward by steward
    We can not do this, because AUTH_RULE txn was reverted
    """
    with pytest.raises(RequestRejectedException, match="Not enough TRUSTEE signatures"):
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
