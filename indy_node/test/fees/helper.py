from indy_common.constants import FEES, SET_FEES, GET_FEE, GET_FEES, FEES_ALIAS
from plenum.common.constants import TXN_TYPE, CURRENT_PROTOCOL_VERSION
from plenum.test.helper import sdk_get_and_check_replies, sdk_gen_request, sdk_sign_and_submit_req_obj


def build_set_fees_request(did, fees):
    op = {TXN_TYPE: SET_FEES,
          FEES: fees}
    return sdk_gen_request(op, protocol_version=CURRENT_PROTOCOL_VERSION,
                           identifier=did)


def build_get_fee(did, alias):
    op = {TXN_TYPE: GET_FEE,
          FEES_ALIAS: alias}
    return sdk_gen_request(op, protocol_version=CURRENT_PROTOCOL_VERSION,
                           identifier=did)


def build_get_fees(did):
    op = {TXN_TYPE: GET_FEES}
    return sdk_gen_request(op, protocol_version=CURRENT_PROTOCOL_VERSION,
                           identifier=did)


def sdk_set_fees(looper, sdk_pool_handle, sdk_wallet, fees):
    req = build_set_fees_request(sdk_wallet[1], fees)
    rep = sdk_sign_and_submit_req_obj(looper, sdk_pool_handle, sdk_wallet, req)
    return sdk_get_and_check_replies(looper, [rep])[0]


def sdk_get_fee(looper, sdk_pool_handle, sdk_wallet, alias):
    req = build_get_fee(sdk_wallet[1], alias)
    rep = sdk_sign_and_submit_req_obj(looper, sdk_pool_handle, sdk_wallet, req)
    return sdk_get_and_check_replies(looper, [rep])[0]


def sdk_get_fees(looper, sdk_pool_handle, sdk_wallet):
    req = build_get_fees(sdk_wallet[1])
    rep = sdk_sign_and_submit_req_obj(looper, sdk_pool_handle, sdk_wallet, req)
    return sdk_get_and_check_replies(looper, [rep])[0]
