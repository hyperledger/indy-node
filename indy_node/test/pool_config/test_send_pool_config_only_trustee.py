from plenum.common.exceptions import RequestRejectedException, RequestNackedException
from plenum.test.helper import sdk_get_bad_response
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from indy_node.test.pool_config.helper import sdk_pool_config_sent
from plenum.common.constants import STEWARD_STRING


def test_only_trustee_send_pool_config_writes_true_force_false(
        nodeSet, looper, sdk_pool_handle, sdk_wallet_trustee, poolConfigWTFF):
    sdk_wallet_steward = sdk_add_new_nym(looper, sdk_pool_handle,
                                         sdk_wallet_trustee, 'tmpname', STEWARD_STRING)
    req = sdk_pool_config_sent(looper, sdk_pool_handle, sdk_wallet_steward, poolConfigWTFF)
    sdk_get_bad_response(looper, [req], RequestRejectedException, 'cannot do')


def test_only_trustee_send_pool_config_writes_false_force_false(
        nodeSet, looper, sdk_pool_handle, sdk_wallet_trustee, poolConfigWFFF):
    sdk_wallet_steward = sdk_add_new_nym(looper, sdk_pool_handle,
                                         sdk_wallet_trustee, 'tmpname', STEWARD_STRING)
    req = sdk_pool_config_sent(looper, sdk_pool_handle, sdk_wallet_steward, poolConfigWFFF)
    sdk_get_bad_response(looper, [req], RequestRejectedException, 'cannot do')


def test_only_trustee_send_pool_config_writes_true_force_true(
        nodeSet, looper, sdk_pool_handle, sdk_wallet_trustee, poolConfigWTFT):
    sdk_wallet_steward = sdk_add_new_nym(looper, sdk_pool_handle,
                                         sdk_wallet_trustee, 'tmpname', STEWARD_STRING)
    req = sdk_pool_config_sent(looper, sdk_pool_handle, sdk_wallet_steward, poolConfigWTFT)
    sdk_get_bad_response(looper, [req], RequestNackedException, 'cannot do')


def test_only_trustee_send_pool_config_writes_false_force_true(
        nodeSet, looper, sdk_pool_handle, sdk_wallet_trustee, poolConfigWFFT):
    sdk_wallet_steward = sdk_add_new_nym(looper, sdk_pool_handle,
                                         sdk_wallet_trustee, 'tmpname', STEWARD_STRING)
    req = sdk_pool_config_sent(looper, sdk_pool_handle, sdk_wallet_steward, poolConfigWFFT)
    sdk_get_bad_response(looper, [req], RequestNackedException, 'cannot do')
