import pytest
from indy import did

from plenum.common.exceptions import RequestRejectedException
from plenum.common.constants import TRUSTEE_STRING
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from plenum.test.helper import sdk_get_and_check_replies, sdk_sign_and_submit_op


def test_new_DID_cannot_update_another_DID(looper,
                                           sdk_pool_handle,
                                           sdk_wallet_trustee,
                                           sdk_wallet_handle):
    """Create trustee"""
    trustee_did, trustee_verkey = looper.loop.run_until_complete(
        did.create_and_store_my_did(sdk_wallet_trustee[0], "{}"))

    """Add trustee to ledger"""
    sdk_add_new_nym(looper, sdk_pool_handle,
                    sdk_wallet_trustee, 'newTrustee', TRUSTEE_STRING, verkey=trustee_verkey, dest=trustee_did)

    """new DID (no role)"""
    new_no_role_did, new_no_role_verkey = looper.loop.run_until_complete(
        did.create_and_store_my_did(sdk_wallet_trustee[0], "{}"))

    """Adding new DID (no role) to ledger"""
    sdk_add_new_nym(looper, sdk_pool_handle,
                    sdk_wallet_trustee,
                    'noRole',
                    verkey=new_no_role_verkey, dest=new_no_role_did)

    """Nym transaction to update Trustee DID that makes no change to verkey or role"""
    op = {'type': '1',
          'dest': trustee_did
          }

    """Submitting the transaction fails"""
    with pytest.raises(RequestRejectedException):
        req = sdk_sign_and_submit_op(looper, sdk_pool_handle, sdk_wallet_trustee, op)
        sdk_get_and_check_replies(looper, [req])
