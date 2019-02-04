import pytest

from plenum.common.exceptions import RequestRejectedException, \
    RequestNackedException

from indy_common.constants import POOL_RESTART, ACTION, START, DATETIME
from plenum.common.constants import TXN_TYPE, STEWARD_STRING
from plenum.test.helper import sdk_gen_request, sdk_sign_and_submit_req_obj, \
    sdk_get_reply, sdk_get_and_check_replies


def test_fail_pool_restart_with_steward_role(
        sdk_pool_handle, sdk_wallet_steward, looper):
    op = {
        TXN_TYPE: POOL_RESTART,
        ACTION: START,
    }
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_steward[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                      sdk_pool_handle,
                                      sdk_wallet_steward,
                                      req_obj)
    with pytest.raises(RequestRejectedException) as excinfo:
        sdk_get_and_check_replies(looper, [req], 100)
    assert excinfo.match('{} can not do this action'.format(STEWARD_STRING))


def test_fail_pool_restart_with_invalid_datetime(
        sdk_pool_handle, sdk_wallet_steward, looper):
    invalid_datetime = "12.05.2018 4/40"
    op = {
        TXN_TYPE: POOL_RESTART,
        ACTION: START,
        DATETIME: invalid_datetime
    }
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_steward[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                      sdk_pool_handle,
                                      sdk_wallet_steward,
                                      req_obj)
    with pytest.raises(RequestNackedException) as excinfo:
        sdk_get_and_check_replies(looper, [req], 100)
    assert excinfo.match("datetime " + invalid_datetime + " is not valid")

