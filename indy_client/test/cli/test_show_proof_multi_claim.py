from collections import OrderedDict

import pytest

from indy_client.cli.cli import IndyCli
from indy_client.client.wallet.connection import Connection


@pytest.fixture()
def claimsUsedForProof():

    claim1Attr = OrderedDict()
    claim1Attr['first_name'] = 'Alice'
    claim1Attr['last_name'] = 'Garcia'
    claim1Attr['account_address_1'] = '321'
    claim1Attr['date_of_birth'] = 'May 15, 1990'

    claim2Attr = OrderedDict()
    claim2Attr['first_name'] = 'Alice'
    claim2Attr['last_name'] = 'Garcia'
    claim2Attr['account_status'] = 'active'

    return [
        (
            Connection(name='Issuer 1'),
            ('TestClaim-1', '0.1', 'Other data'),
            claim1Attr
        ),
        (
            Connection(name='Issuer 2'),
            ('TestClaim-2', '0.1', 'Other claim 2 data'),
            claim2Attr
        )
    ]


@pytest.fixture()
def proofRequestAttrs():
    return {
        'first_name': None,
        'last_name': None,
        'account_status': None
    }


def test_showProofOnlyUsedAttributesAreHighlighted(
        claimsUsedForProof, proofRequestAttrs):
    actualConstructionToPrint = IndyCli._printClaimsUsedInProofConstruction(
        claimsUsedForProof, proofRequestAttrs
    )

    expectedPrint = '\nThe Proof is constructed from the following claims:\n' \
                    '\n    Claim [1] (TestClaim-1 v0.1 from Issuer 1)\n' \
                    '        * first_name: Alice\n' \
                    '        * last_name: Garcia\n' \
                    '          account_address_1: 321\n' \
                    '          date_of_birth: May 15, 1990\n' \
                    '\n    Claim [2] (TestClaim-2 v0.1 from Issuer 2)\n' \
                    '          first_name: Alice\n' \
                    '          last_name: Garcia\n' \
                    '        * account_status: active\n'

    assert expectedPrint == actualConstructionToPrint
