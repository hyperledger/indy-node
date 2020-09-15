import pytest

from indy_node.test.suspension.helper import sdk_suspend_role
from indy_node.test.suspension.test_suspension import another_trustee

from plenum.common.exceptions import RequestRejectedException, RequestNackedException
from plenum.test.pool_transactions.helper import sdk_add_new_nym


@pytest.mark.suspension
def test_trustee_suspending_endorser(looper, sdk_pool_handle, sdk_wallet_trustee,
                                     sdk_wallet_endorser):
    _, did = sdk_wallet_endorser
    sdk_suspend_role(looper, sdk_pool_handle, sdk_wallet_trustee, did)
    with pytest.raises(RequestRejectedException) as e:
        sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_endorser)
    e.match('Rule for this action is')


@pytest.mark.suspension
def test_trustee_suspending_trustee(looper, sdk_pool_handle, sdk_wallet_trustee,
                                 another_trustee):
    _, did = another_trustee
    sdk_suspend_role(looper, sdk_pool_handle, sdk_wallet_trustee, did)
    with pytest.raises(RequestRejectedException) as e:
        sdk_add_new_nym(looper, sdk_pool_handle, another_trustee)
    e.match('Rule for this action is')


@pytest.mark.suspension
def test_trustee_suspending_steward(looper, sdk_pool_handle, sdk_wallet_trustee,
                                 sdk_wallet_steward):
    _, did = sdk_wallet_steward
    sdk_suspend_role(looper, sdk_pool_handle, sdk_wallet_trustee, did)
    with pytest.raises(RequestRejectedException) as e:
        sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_steward)
    e.match('Rule for this action is')


@pytest.mark.suspension
def test_endorser_suspending_himself_by_verkey_flush(looper, sdk_pool_handle,
                                                  sdk_wallet_endorser):
    # The endorser has already lost its role due to previous tests,
    # but it is ok for this test where the endorser flushes its verkey
    # and then he is unable to send NYM due to empty verkey.
    _, did = sdk_wallet_endorser
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_endorser, dest=did, verkey='')
    with pytest.raises(RequestNackedException) as e:
        sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_endorser)
    e.match('insufficient number of valid signatures')
