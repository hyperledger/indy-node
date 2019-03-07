import pytest

from indy_common.authorize.auth_actions import ADD_PREFIX
from indy_common.authorize.auth_constraints import CONSTRAINT_ID, SIG_COUNT, NEED_TO_BE_OWNER, METADATA, \
    ConstraintsEnum, ROLE, AUTH_CONSTRAINTS
from indy_common.authorize.auth_map import auth_map
from indy_common.constants import AUTH_RULE, NYM, TRUST_ANCHOR, CONSTRAINT, AUTH_ACTION, AUTH_TYPE, FIELD, NEW_VALUE, \
    OLD_VALUE, GET_AUTH_RULE
from indy_common.types import ConstraintEntityField
from indy_node.server.config_req_handler import ConfigReqHandler
from plenum.common.constants import TXN_TYPE, TRUSTEE, STEWARD, DATA, KEY
from plenum.common.exceptions import RequestRejectedException, \
    RequestNackedException
from plenum.test.helper import sdk_gen_request, sdk_sign_and_submit_req_obj, sdk_get_and_check_replies


def sdk_get_auth_rule_request(looper, sdk_wallet_trustee, sdk_pool_handle, key=None):
    op = {TXN_TYPE: GET_AUTH_RULE}
    if key:
        op.update(key)
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                      sdk_pool_handle,
                                      sdk_wallet_trustee,
                                      req_obj)
    resp = sdk_get_and_check_replies(looper, [req])
    return resp


def generate_key(auth_action=ADD_PREFIX, auth_type=NYM,
                 field=ROLE, new_value=TRUST_ANCHOR,
                 old_value=None):
    key = {AUTH_ACTION: auth_action,
           AUTH_TYPE: auth_type,
           FIELD: field,
           NEW_VALUE: new_value,
           }
    if old_value:
        key[OLD_VALUE] = old_value
    return key


def test_get_one_auth_rule_transaction(looper,
                                       sdk_wallet_trustee,
                                       sdk_pool_handle):
    key = generate_key()
    str_key = ConfigReqHandler.get_auth_key(key)
    req, resp = sdk_get_auth_rule_request(looper,
                                          sdk_wallet_trustee,
                                          sdk_pool_handle,
                                          key)[0]
    assert auth_map.get(str_key).as_dict == resp["result"][DATA]
    assert str_key == resp["result"][KEY]


def test_get_one_auth_rule_transaction_after_write(looper,
                                                   sdk_wallet_trustee,
                                                   sdk_pool_handle):
    resp = sdk_get_auth_rule_request(looper,
                                     sdk_wallet_trustee,
                                     sdk_pool_handle)
    print(resp)


def test_get_all_auth_rule_transactions(looper,
                                        sdk_wallet_trustee,
                                        sdk_pool_handle):
    resp = sdk_get_auth_rule_request(looper,
                                     sdk_wallet_trustee,
                                     sdk_pool_handle)
    print(resp)
