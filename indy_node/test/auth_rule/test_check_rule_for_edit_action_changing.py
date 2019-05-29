import pytest

from indy_common.authorize.auth_actions import EDIT_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_node.test.auth_rule.helper import create_verkey_did, sdk_send_and_check_auth_rule_request
from plenum.common.constants import STEWARD_STRING, STEWARD, NYM, ROLE
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import sdk_sign_and_submit_op, sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import sdk_add_new_nym


def test_check_rule_for_edit_action_changing(looper,
                                             sdk_wallet_trustee,
                                             sdk_wallet_steward,
                                             sdk_pool_handle):
    wh, _ = sdk_wallet_trustee
    new_steward_did, new_steward_verkey = create_verkey_did(looper, wh)
    """Adding new steward for old auth rules"""
    sdk_add_new_nym(looper,
                    sdk_pool_handle,
                    sdk_wallet_trustee,
                    'newSteward1',
                    STEWARD_STRING,
                    dest=new_steward_did, verkey=new_steward_verkey)

    constraint = AuthConstraint(role=STEWARD,
                                sig_count=1)
    """Change role from steward to '' (blacklisting STEWARD) can only STEWARD"""
    sdk_send_and_check_auth_rule_request(looper, sdk_pool_handle, sdk_wallet_trustee,
                                         auth_action=EDIT_PREFIX,
                                         auth_type=NYM, field=ROLE, new_value='', old_value=STEWARD,
                                         constraint=constraint.as_dict)
    op = {'type': '1',
          'dest': new_steward_did,
          'role': None}
    with pytest.raises(RequestRejectedException, match="Not enough STEWARD signatures"):
        """Blacklisting new steward by TRUSTEE"""
        req = sdk_sign_and_submit_op(looper, sdk_pool_handle, sdk_wallet_trustee, op)
        sdk_get_and_check_replies(looper, [req])
    """We change auth rules and for now only steward can add new steward"""
    req = sdk_sign_and_submit_op(looper, sdk_pool_handle, sdk_wallet_steward, op)
    sdk_get_and_check_replies(looper, [req])
