import pytest
from sovrin_client.client.wallet.link import Link


@pytest.mark.skip(reason='INDY-105')
def test_link_has_requested_proofs():
    testLink = Link("Test")

    # testLink.requestedProofs