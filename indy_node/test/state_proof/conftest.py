import pytest

from plenum.test.delayers import req_delay


@pytest.fixture(scope="module")
def nodeSetWithOneNodeResponding(nodeSet):
    # the order of nodes the client sends requests to is [Alpha, Beta, Gamma, Delta]
    # delay all requests to Beta, Gamma and Delta
    # we expect that it's sufficient for the client to get Reply from Alpha only
    # as for write requests, we can send it to 1 node only, and it will be propagated to others
    for node in nodeSet[1:]:
        node.clientIbStasher.delay(req_delay())
    return nodeSet
