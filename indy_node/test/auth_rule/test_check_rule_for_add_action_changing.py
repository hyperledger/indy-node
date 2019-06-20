import pytest

from indy_common.authorize.auth_actions import ADD_PREFIX
from indy_common.authorize.auth_constraints import ROLE, AuthConstraint
from indy_common.constants import NYM
from indy_node.test.auth_rule.helper import create_verkey_did, sdk_send_and_check_auth_rule_request
from plenum.common.constants import STEWARD, STEWARD_STRING
from plenum.common.exceptions import RequestRejectedException
from plenum.test.pool_transactions.helper import sdk_add_new_nym


def test_check_rule_for_add_action_changing(looper,
                                            sdk_wallet_trustee,
                                            sdk_wallet_steward,
                                            sdk_pool_handle):
    wh, _ = sdk_wallet_trustee
    did1, verkey1 = create_verkey_did(looper, wh)
    """Adding new steward for old auth rules"""
    sdk_add_new_nym(looper,
                    sdk_pool_handle,
                    sdk_wallet_trustee,
                    'newSteward1',
                    STEWARD_STRING,
                    dest=did1, verkey=verkey1)

    constraint = AuthConstraint(role=STEWARD,
                                sig_count=1)
    sdk_send_and_check_auth_rule_request(looper, sdk_pool_handle, sdk_wallet_trustee,
                                         auth_action=ADD_PREFIX,
                                         auth_type=NYM, field=ROLE, new_value=STEWARD, old_value=None,
                                         constraint=constraint.as_dict)

    did2, verkey2 = create_verkey_did(looper, wh)
    with pytest.raises(RequestRejectedException, match="Not enough STEWARD signatures"):
        """Adding new steward for changed auth rules"""
        sdk_add_new_nym(looper,
                        sdk_pool_handle,
                        sdk_wallet_trustee,
                        'newSteward2',
                        STEWARD_STRING,
                        dest=did2, verkey=verkey2)
    """We change auth rules and for now only steward can add new steward"""
    sdk_add_new_nym(looper,
                    sdk_pool_handle,
                    sdk_wallet_steward,
                    'newSteward2',
                    STEWARD_STRING,
                    dest=did2, verkey=verkey2)
