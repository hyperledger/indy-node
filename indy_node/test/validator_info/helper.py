import json

from indy.did import create_and_store_my_did
from indy.ledger import build_get_validator_info_request

from indy_node.test.pool_restart.helper import sdk_get_and_check_multiply_replies
from plenum.common.util import randomString
from plenum.test.pool_transactions.helper import sdk_sign_and_send_prepared_request


def sdk_get_validator_info(looper, steward_wallet, sdk_pool_handle, seed=None):
    # filling validator_info request and getting steward did
    seed = seed or randomString(32)
    validator_info_request, did = looper.loop.run_until_complete(
        prepare_validator_info_request(steward_wallet, seed))

    # sending request using 'sdk_' functions
    request_couple = sdk_sign_and_send_prepared_request(looper, steward_wallet,
                                                        sdk_pool_handle,
                                                        validator_info_request)
    # waiting for replies
    return sdk_get_and_check_multiply_replies(looper, request_couple)


async def prepare_validator_info_request(wallet, named_seed):
    wh, submitter_did = wallet
    (named_did, named_verkey) = \
        await create_and_store_my_did(wh, json.dumps({'seed': named_seed}))
    restart_request = await build_get_validator_info_request(submitter_did)
    return restart_request, named_did