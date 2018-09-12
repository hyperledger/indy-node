from plenum.test.helper import sdk_sign_and_submit_req_obj, \
    sdk_get_and_check_replies
from indy_client.client.wallet.pool_config import PoolConfig as WPoolConfig


def sdk_pool_config_sent(looper, sdk_pool_handle, sdk_wallet_trustee, pool_config_data):
    _, did = sdk_wallet_trustee
    pool_cfg = WPoolConfig(trustee=did, **pool_config_data)
    req = pool_cfg.ledgerRequest()
    req = sdk_sign_and_submit_req_obj(looper, sdk_pool_handle, sdk_wallet_trustee, req)
    return pool_cfg, req


def sdk_ensure_pool_config_sent(looper, sdk_pool_handle, sdk_wallet_trustee, pool_config_data):
    _, did = sdk_wallet_trustee
    pool_cfg = WPoolConfig(trustee=did, **pool_config_data)
    req = pool_cfg.ledgerRequest()
    req = sdk_sign_and_submit_req_obj(looper, sdk_pool_handle, sdk_wallet_trustee, req)
    sdk_get_and_check_replies(looper, [req])
    return pool_cfg


def check_pool_config_writable_set(nodes, writable):
    for node in nodes:
        assert node.poolCfg.isWritable() == writable
