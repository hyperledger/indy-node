import pytest
from indy import did

from indy_common.constants import TRUST_ANCHOR_STRING
from plenum.common.constants import TRUSTEE_STRING, STEWARD_STRING
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import sdk_get_and_check_replies, sdk_sign_and_submit_op
from plenum.test.pool_transactions.helper import sdk_add_new_nym


def test_steward_suspension_by_another_trustee(looper,
                                               sdk_pool_handle,
                                               sdk_wallet_trustee,
                                               sdk_wallet_handle,
                                               with_verkey):
    new_trustee_did, new_trustee_verkey = looper.loop.run_until_complete(
        did.create_and_store_my_did(sdk_wallet_trustee[0], "{}"))
    new_steward_did, new_steward_verkey = looper.loop.run_until_complete(
        did.create_and_store_my_did(sdk_wallet_trustee[0], "{}"))

    """Adding new steward"""
    sdk_add_new_nym(looper, sdk_pool_handle,
                    sdk_wallet_trustee, 'newSteward', STEWARD_STRING, verkey=new_steward_verkey, dest=new_steward_did)

    """Adding new trustee"""
    sdk_add_new_nym(looper, sdk_pool_handle,
                    sdk_wallet_trustee, 'newTrustee', TRUSTEE_STRING, verkey=new_trustee_verkey, dest=new_trustee_did)

    """Blacklisting new steward by new trustee"""
    op = {'type': '1',
          'dest': new_steward_did,
          'role': None}
    if with_verkey:
        op['verkey'] = new_steward_verkey
    req = sdk_sign_and_submit_op(looper, sdk_pool_handle, (sdk_wallet_handle, new_trustee_did), op)
    if with_verkey:
        with pytest.raises(RequestRejectedException):
            sdk_get_and_check_replies(looper, [req])
    else:
        sdk_get_and_check_replies(looper, [req])


def test_steward_cannot_create_trust_anchors_after_demote(looper,
                                                          sdk_pool_handle,
                                                          sdk_wallet_trustee,
                                                          sdk_wallet_handle):
    new_steward_did, new_steward_verkey = looper.loop.run_until_complete(
        did.create_and_store_my_did(sdk_wallet_trustee[0], "{}"))
    new_ta_did, new_ta_verkey = looper.loop.run_until_complete(
        did.create_and_store_my_did(sdk_wallet_trustee[0], "{}"))
    new_ta_2_did, new_ta_2_verkey = looper.loop.run_until_complete(
        did.create_and_store_my_did(sdk_wallet_trustee[0], "{}"))

    """Adding new steward"""
    sdk_add_new_nym(looper, sdk_pool_handle,
                    sdk_wallet_trustee,
                    'newSteward',
                    STEWARD_STRING,
                    verkey=new_steward_verkey, dest=new_steward_did)

    """Adding new TA"""
    sdk_add_new_nym(looper, sdk_pool_handle,
                    (sdk_wallet_handle, new_steward_did),
                    'newSteward',
                    TRUST_ANCHOR_STRING,
                    verkey=new_ta_verkey, dest=new_ta_did)

    """Blacklisting new steward by trustee"""
    op = {'type': '1',
          'dest': new_steward_did,
          'role': None}
    req = sdk_sign_and_submit_op(looper, sdk_pool_handle, sdk_wallet_trustee, op)
    sdk_get_and_check_replies(looper, [req])

    """Try to add new TA by previous demoted steward"""
    with pytest.raises(RequestRejectedException):
        sdk_add_new_nym(looper, sdk_pool_handle,
                        (sdk_wallet_handle, new_steward_did),
                        'newSteward',
                        TRUST_ANCHOR_STRING,
                        verkey=new_ta_2_verkey, dest=new_ta_2_did)
