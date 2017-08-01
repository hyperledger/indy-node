import pytest

from sovrin_client.test.helper import getClientAddedWithRole
from sovrin_node.test.did.helper import updateSovrinIdrWithVerkey


@pytest.fixture(scope="module")
def some_transactions_done(looper, nodeSet, tdirWithPoolTxns, trustee,
                           trusteeWallet):
    new_c, new_w = getClientAddedWithRole(nodeSet, tdirWithPoolTxns, looper,
                                          trustee, trusteeWallet, 'some_name',
                                          addVerkey=False)
    new_idr = new_w.defaultId
    updateSovrinIdrWithVerkey(looper, trusteeWallet, trustee,
                              new_idr, new_w.getVerkey(new_idr))
    # TODO: Since empty verkey and absence of verkey are stored in the ledger
    # in the same manner, this fails during catchup since the nodes that
    # processed the transaction saw verkey as `''` but while deserialising the
    # ledger they cannot differentiate between None and empty string.
    # updateSovrinIdrWithVerkey(looper, new_w, new_c,
    #                           new_idr, '')