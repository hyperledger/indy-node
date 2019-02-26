import pytest

from indy_common.authorize.auth_actions import ADD_PREFIX
from indy_common.authorize.auth_constraints import CONSTRAINT_ID, SIG_COUNT, NEED_TO_BE_OWNER, METADATA, \
    ConstraintsEnum, ROLE, AUTH_CONSTRAINTS
from indy_common.constants import AUTH_RULE, NYM, TRUST_ANCHOR, CONSTRAINT, AUTH_ACTION, AUTH_TYPE, FIELD, NEW_VALUE, \
    OLD_VALUE, GET_AUTH_RULE
from indy_common.types import ConstraintEntityField
from plenum.common.constants import TXN_TYPE, TRUSTEE, STEWARD
from plenum.common.exceptions import RequestRejectedException, \
    RequestNackedException
from plenum.test.helper import sdk_gen_request, sdk_sign_and_submit_req_obj, sdk_get_and_check_replies


def sdk_get_auth_rule_request(looper, sdk_wallet_trustee, sdk_pool_handle):
    op = {TXN_TYPE: GET_AUTH_RULE}
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                      sdk_pool_handle,
                                      sdk_wallet_trustee,
                                      req_obj)
    resp = sdk_get_and_check_replies(looper, [req])
    return resp


def test_auth_rule_transaction(looper,
                               sdk_wallet_trustee,
                               sdk_pool_handle):
    resp = sdk_get_auth_rule_request(looper,
                              sdk_wallet_trustee,
                              sdk_pool_handle)
    print(resp)
