from indy.ledger import build_pool_config_request

from plenum.test.helper import sdk_get_and_check_replies, sdk_sign_and_submit_req


def sdk_pool_config_sent(looper, sdk_pool_handle, sdk_wallet_trustee, pool_config_data):
    _, did = sdk_wallet_trustee
    req = looper.loop.run_until_complete(build_pool_config_request(
        did, pool_config_data['writes'], pool_config_data['force']))
    req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, req)
    return req



def sdk_ensure_pool_config_sent(looper, sdk_pool_handle, sdk_wallet_trustee, pool_config_data):
    _, did = sdk_wallet_trustee
    req = looper.loop.run_until_complete(build_pool_config_request(
        did, pool_config_data['writes'], pool_config_data['force']))
    req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, req)
    rep = sdk_get_and_check_replies(looper, [req])
    return rep


def check_pool_config_writable_set(nodes, writable):
    for node in nodes:
        assert node.poolCfg.isWritable() == writable
