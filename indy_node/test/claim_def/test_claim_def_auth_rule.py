import json

import pytest
from indy.ledger import build_get_schema_request, parse_get_schema_response

from indy_node.test.auth_rule.auth_framework.claim_def import get_schema_json
from plenum.common.exceptions import RequestRejectedException

from indy_node.test.claim_def.test_send_claim_def import sdk_send_claim_def
from plenum.common.types import OPERATION

from indy_node.test.api.helper import sdk_write_schema

from indy_node.test.helper import build_auth_rule_request_json
from plenum.common.constants import TRUSTEE, STEWARD, DATA

from indy_common.authorize.auth_actions import ADD_PREFIX, EDIT_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_common.constants import CLAIM_DEF

from plenum.test.helper import sdk_get_and_check_replies, \
    sdk_get_reply, sdk_sign_and_submit_req, sdk_sign_and_submit_op
from indy_node.test.auth_rule.helper import sdk_send_and_check_req_json


def send_and_check(looper, sdk_pool_handle, req_json, wallet):
    return sdk_send_and_check_req_json(
        looper, sdk_pool_handle, wallet, req_json)[0]


def test_auth_rule_transaction_for_edit(looper,
                                        txnPoolNodeSet,
                                        sdk_wallet_trustee,
                                        sdk_wallet_steward,
                                        sdk_pool_handle):
    constraint = AuthConstraint(role=STEWARD,
                                sig_count=1,
                                need_to_be_owner=False)
    req1 = build_auth_rule_request_json(
        looper, sdk_wallet_trustee[1],
        auth_action=ADD_PREFIX,
        auth_type=CLAIM_DEF,
        field='*',
        new_value='*',
        constraint=constraint.as_dict
    )

    send_and_check(looper, sdk_pool_handle, req1, wallet=sdk_wallet_trustee)

    constraint = AuthConstraint(role=TRUSTEE,
                                sig_count=1,
                                need_to_be_owner=False)
    req2 = build_auth_rule_request_json(
        looper, sdk_wallet_trustee[1],
        auth_action=EDIT_PREFIX,
        auth_type=CLAIM_DEF,
        field='*',
        old_value='*',
        new_value='*',
        constraint=constraint.as_dict
    )

    send_and_check(looper, sdk_pool_handle, req2, wallet=sdk_wallet_trustee)

    schema_json = get_schema_json(looper, sdk_pool_handle, sdk_wallet_trustee)

    reply = sdk_send_claim_def(looper, sdk_pool_handle, sdk_wallet_steward, 'tag_1', schema_json)

    req = reply[0][0]
    req[OPERATION][DATA]['primary']['n'] = 'abc'

    with pytest.raises(RequestRejectedException):
        resp = sdk_sign_and_submit_op(looper, sdk_pool_handle, sdk_wallet_steward, op=req[OPERATION])
        sdk_get_and_check_replies(looper, [resp])
