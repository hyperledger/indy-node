import json

from plenum.common.constants import TXN_TYPE, CURRENT_PROTOCOL_VERSION
from plenum.test.helper import sdk_sign_and_submit_req, sdk_get_and_check_replies, sdk_gen_request, \
    sdk_sign_request_objects, sdk_send_signed_requests, sdk_sign_and_submit_req_obj
from indy_common.constants import LEDGERS_FREEZE, GET_FROZEN_LEDGERS, LEDGERS_IDS


def build_freeze_ledgers_request(did, ledgers_ids: [str]):
    op = {TXN_TYPE: "123",
          LEDGERS_IDS: ledgers_ids}
    return sdk_gen_request(op, protocol_version=CURRENT_PROTOCOL_VERSION,
                    identifier=did)


def build_get_frozen_ledgers_request(did):
    op = {TXN_TYPE: "124"}
    return sdk_gen_request(op, protocol_version=CURRENT_PROTOCOL_VERSION,
                    identifier=did)


def sdk_send_freeze_ledgers(looper, sdk_pool_handle, sdk_wallets, ledgers_ids: [str]):
    # req = looper.loop.run_until_complete(build_freeze_ledgers_request(sdk_wallets[0][1], ledgers_ids))  # json.dumps(params)
    # sdk_multi_sign_request_objects
    req = build_freeze_ledgers_request(sdk_wallets[0][1], ledgers_ids)  # json.dumps(params)
    s_req = None
    for sdk_wallet in sdk_wallets:
        s_req = sdk_sign_request_objects(looper, sdk_wallet, [req])[0]
    return sdk_send_signed_requests(sdk_pool_handle, [s_req])[0]


def sdk_get_frozen_ledgers(looper, sdk_pool_handle, sdk_wallet):
    # req = looper.loop.run_until_complete(build_get_frozen_ledgers_request(sdk_wallet[1]))
    req = build_get_frozen_ledgers_request(sdk_wallet[1])
    rep = sdk_sign_and_submit_req_obj(looper, sdk_pool_handle, sdk_wallet, req)
    return sdk_get_and_check_replies(looper, [rep])[0]
