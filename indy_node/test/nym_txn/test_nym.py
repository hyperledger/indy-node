import pytest
from indy_common.constants import ENDORSER_STRING

from plenum.common.exceptions import RequestRejectedException

from plenum.test.pool_transactions.helper import sdk_add_new_nym


def testStewardCreatesAEndorser(looper, sdk_pool_handle, sdk_wallet_steward):
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_steward, role=ENDORSER_STRING)


# FIXME why is it necessary to check
def testStewardCreatesAnotherEndorser(looper, sdk_pool_handle, sdk_wallet_steward):
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_steward, role=ENDORSER_STRING)
