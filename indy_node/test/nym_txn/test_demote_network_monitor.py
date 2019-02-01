import pytest
from indy import did

from indy_common.constants import NETWORK_MONITOR
from indy_node.test.validator_info.helper import sdk_get_validator_info
from plenum.common.constants import STEWARD_STRING
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import sdk_sign_and_submit_op, sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import sdk_add_new_nym


def test_network_monitor_suspension_by_another_steward(looper,
                                                       sdk_pool_handle,
                                                       sdk_wallet_steward,
                                                       sdk_wallet_trustee,
                                                       sdk_wallet_handle,
                                                       with_verkey):
    new_steward_did, new_steward_verkey = looper.loop.run_until_complete(
        did.create_and_store_my_did(sdk_wallet_trustee[0], "{}"))
    new_network_monitor_did, new_network_monitor_verkey = looper.loop.run_until_complete(
        did.create_and_store_my_did(sdk_wallet_steward[0], "{}"))

    """Adding new steward"""
    sdk_add_new_nym(looper, sdk_pool_handle,
                    sdk_wallet_trustee, 'newSteward', STEWARD_STRING, verkey=new_steward_verkey, dest=new_steward_did)

    """Adding NETWORK_MONITOR role by first steward"""
    op = {'type': '1',
          'dest': new_network_monitor_did,
          'role': NETWORK_MONITOR,
          'verkey': new_network_monitor_verkey}
    req = sdk_sign_and_submit_op(looper, sdk_pool_handle, (sdk_wallet_handle, new_steward_did), op)
    sdk_get_and_check_replies(looper, [req])

    """Check that get_validator_info command works for NETWORK_MONITOR role"""
    sdk_get_validator_info(looper, (sdk_wallet_handle, new_network_monitor_did), sdk_pool_handle)

    """Blacklisting network_monitor by new steward"""
    op = {'type': '1',
          'dest': new_network_monitor_did,
          'role': None}
    if with_verkey:
        op['verkey'] = new_network_monitor_verkey
    req = sdk_sign_and_submit_op(looper, sdk_pool_handle, (sdk_wallet_handle, new_steward_did), op)
    if with_verkey:
        with pytest.raises(RequestRejectedException):
            sdk_get_and_check_replies(looper, [req])
    else:
        sdk_get_and_check_replies(looper, [req])
        with pytest.raises(RequestRejectedException):
            sdk_get_validator_info(looper, (sdk_wallet_handle, new_network_monitor_did), sdk_pool_handle)


def test_network_monitor_suspension_by_itself(looper,
                                              sdk_pool_handle,
                                              sdk_wallet_steward,
                                              sdk_wallet_handle,
                                              with_verkey):
    new_network_monitor_did, new_network_monitor_verkey = looper.loop.run_until_complete(
        did.create_and_store_my_did(sdk_wallet_steward[0], "{}"))

    """Adding NETWORK_MONITOR role by steward"""
    op = {'type': '1',
          'dest': new_network_monitor_did,
          'role': NETWORK_MONITOR,
          'verkey': new_network_monitor_verkey}
    req = sdk_sign_and_submit_op(looper, sdk_pool_handle, (sdk_wallet_handle, sdk_wallet_steward[1]), op)
    sdk_get_and_check_replies(looper, [req])

    """Blacklisting network_monitor by itself"""
    op = {'type': '1',
          'dest': new_network_monitor_did,
          'role': None}
    if with_verkey:
        op['verkey'] = new_network_monitor_verkey
    req = sdk_sign_and_submit_op(looper, sdk_pool_handle, (sdk_wallet_handle, new_network_monitor_did), op)
    with pytest.raises(RequestRejectedException):
        sdk_get_and_check_replies(looper, [req])
