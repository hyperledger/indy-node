import json

from indy.payment import build_set_txn_fees_req

from indy_common.constants import FEES, SET_FEES
from plenum.common.constants import TXN_TYPE, CURRENT_PROTOCOL_VERSION, LEDGERS_FREEZE, LEDGERS_IDS, GET_FROZEN_LEDGERS
from plenum.test.helper import sdk_get_and_check_replies, sdk_gen_request, \
    sdk_send_signed_requests, sdk_sign_and_submit_req_obj, sdk_multi_sign_request_objects


def build_set_fees_request(did, fees):
    op = {TXN_TYPE: SET_FEES,
          FEES: fees}
    return sdk_gen_request(op, protocol_version=CURRENT_PROTOCOL_VERSION,
                           identifier=did)


def build_get_frozen_ledgers_request(did):
    op = {TXN_TYPE: GET_FROZEN_LEDGERS}
    return sdk_gen_request(op, protocol_version=CURRENT_PROTOCOL_VERSION,
                           identifier=did)


def sdk_set_fees(looper, sdk_pool_handle, sdk_wallet, fees):
    req = build_set_fees_request(sdk_wallet[1], fees)
    rep = sdk_sign_and_submit_req_obj(looper, sdk_pool_handle, sdk_wallet, req)
    return sdk_get_and_check_replies(looper, [rep])[0]


def sdk_get_frozen_ledgers(looper, sdk_pool_handle, sdk_wallet):
    req = build_get_frozen_ledgers_request(sdk_wallet[1])
    rep = sdk_sign_and_submit_req_obj(looper, sdk_pool_handle, sdk_wallet, req)
    return sdk_get_and_check_replies(looper, [rep])[0]
