import pytest

from indy_client.test.helper import getClientAddedWithRole
from indy_node.test.did.helper import updateIndyIdrWithVerkey


@pytest.fixture(scope="module")
def some_transactions_done(looper, nodeSet, tdirWithClientPoolTxns, trustee,
                           trusteeWallet):
    new_c, new_w = getClientAddedWithRole(nodeSet, tdirWithClientPoolTxns, looper,
                                          trustee, trusteeWallet, 'some_name',
                                          addVerkey=False)
    new_idr = new_w.defaultId
    updateIndyIdrWithVerkey(looper, trusteeWallet, trustee,
                            new_idr, new_w.getVerkey(new_idr))
    # TODO: Since empty verkey and absence of verkey are stored in the ledger
    # in the same manner, this fails during catchup since the nodes that
    # processed the transaction saw verkey as `''` but while deserialising the
    # ledger they cannot differentiate between None and empty string.
    # updateIndyIdrWithVerkey(looper, new_w, new_c,
    #                           new_idr, '')
