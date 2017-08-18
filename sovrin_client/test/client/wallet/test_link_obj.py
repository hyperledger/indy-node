import pytest
from sovrin_client.client.wallet.connection import Connection


@pytest.mark.skip(reason='INDY-105')
def test_link_has_requested_proofs():
    testLink = Connection("Test")

    # testLink.requestedProofs
