import pytest

from common.serializers.serialization import config_state_serializer
from indy_common.authorize.auth_actions import ADD_PREFIX, AuthActionAdd
from indy_common.authorize.auth_constraints import AuthConstraint, ConstraintsSerializer
from indy_common.constants import NYM, CONFIG_LEDGER_ID
from indy_common.state import config
from indy_node.test.auth_rule.helper import create_verkey_did, sdk_send_and_check_auth_rule_request
from plenum.common.constants import STEWARD, ROLE, STEWARD_STRING
from plenum.common.exceptions import RequestRejectedException
from plenum.common.startable import Mode
from plenum.test.delayers import cDelay, ppDelay, pDelay
from plenum.test.helper import assertExp
from plenum.test.node_catchup.helper import ensure_all_nodes_have_same_data
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from plenum.test.stasher import delay_rules_without_processing
from stp_core.loop.eventually import eventually


def test_catching_up_auth_rule_txn(looper,
                                   txnPoolNodeSet,
                                   sdk_wallet_trustee,
                                   sdk_wallet_steward,
                                   sdk_pool_handle):
    delayed_node = txnPoolNodeSet[-1]
    wh, _ = sdk_wallet_trustee
    new_steward_did, new_steward_verkey = create_verkey_did(looper, wh)
    changed_constraint = AuthConstraint(role=STEWARD,
                                        sig_count=1)
    action = AuthActionAdd(txn_type=NYM,
                           field=ROLE,
                           value=STEWARD)
    with pytest.raises(RequestRejectedException, match="Not enough TRUSTEE signatures"):
        sdk_add_new_nym(looper,
                        sdk_pool_handle,
                        sdk_wallet_steward,
                        'newSteward2',
                        STEWARD_STRING,
                        dest=new_steward_did, verkey=new_steward_verkey)
    with delay_rules_without_processing(delayed_node.nodeIbStasher, cDelay(), pDelay(), ppDelay()):
        sdk_send_and_check_auth_rule_request(looper, sdk_pool_handle, sdk_wallet_trustee,
                                             auth_action=ADD_PREFIX,
                                             auth_type=action.txn_type, field=action.field,
                                             new_value=action.value, old_value=None,
                                             constraint=changed_constraint.as_dict)
        sdk_add_new_nym(looper,
                        sdk_pool_handle,
                        sdk_wallet_trustee,
                        'newSteward2')
        delayed_node.start_catchup()
        looper.run(eventually(lambda: assertExp(delayed_node.mode == Mode.participating)))
    sdk_add_new_nym(looper,
                    sdk_pool_handle,
                    sdk_wallet_steward,
                    'newSteward3',
                    STEWARD_STRING,
                    dest=new_steward_did, verkey=new_steward_verkey)
    ensure_all_nodes_have_same_data(looper, txnPoolNodeSet)
    config_state = delayed_node.states[CONFIG_LEDGER_ID]
    from_state = config_state.get(config.make_state_path_for_auth_rule(action.get_action_id()),
                                  isCommitted=True)
    assert changed_constraint == ConstraintsSerializer(config_state_serializer).deserialize(from_state)
