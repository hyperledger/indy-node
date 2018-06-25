import pytest

from plenum.test.pool_transactions.helper import sdk_add_new_nym


@pytest.fixture(scope="module")
def some_transactions_done(looper, nodeSet, sdk_pool_handle,
                           sdk_wallet_trustee):
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee)
    # TODO: Since empty verkey and absence of verkey are stored in the ledger
    # in the same manner, this fails during catchup since the nodes that
    # processed the transaction saw verkey as `''` but while deserialising the
    # ledger they cannot differentiate between None and empty string.
    # updateIndyIdrWithVerkey(looper, new_w, new_c,
    #                           new_idr, '')
