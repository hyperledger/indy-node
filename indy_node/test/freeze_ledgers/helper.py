from plenum.common.constants import TXN_TYPE, CURRENT_PROTOCOL_VERSION
from plenum.test.helper import sdk_sign_and_submit_req, sdk_get_and_check_replies, sdk_gen_request
from indy_common.constants import LEDGERS_FREEZE, GET_FROZEN_LEDGERS, LEDGERS_IDS


def build_freeze_ledgers_request(did, ledgers_ids: [str]):
    op = {TXN_TYPE: LEDGERS_FREEZE,
          LEDGERS_IDS: ledgers_ids}
    sdk_gen_request(op, protocol_version=CURRENT_PROTOCOL_VERSION,
                    identifier=did)


def build_get_frozen_ledgers_request(did):
    op = {TXN_TYPE: GET_FROZEN_LEDGERS}
    sdk_gen_request(op, protocol_version=CURRENT_PROTOCOL_VERSION,
                    identifier=did)


def sdk_send_freeze_ledgers(looper, sdk_pool_handle, sdk_wallet, ledgers_ids: [str]):
    req = looper.loop.run_until_complete(build_freeze_ledgers_request(sdk_wallet[1], ledgers_ids))  # json.dumps(params)
    rep = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet, req)
    return sdk_get_and_check_replies(looper, [rep])[0]


def sdk_get_frozen_ledgers(looper, sdk_pool_handle, sdk_wallet):
    req = looper.loop.run_until_complete(build_get_frozen_ledgers_request(sdk_wallet[1]))
    rep = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet, req)
    return sdk_get_and_check_replies(looper, [rep])[0]
