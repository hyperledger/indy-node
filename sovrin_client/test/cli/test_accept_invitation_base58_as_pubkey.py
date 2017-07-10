import json

import pytest

from plenum.common.constants import PUBKEY

# noinspection PyUnresolvedReferences
from sovrin_client.test.cli.conftest \
    import faberMap as faberMapWithoutEndpointPubkey

# noinspection PyUnresolvedReferences
from sovrin_client.test.cli.test_tutorial import aliceAcceptedFaberInvitation, \
    aliceCli, preRequisite, faberCli, acmeCli, thriftCli, faberWithEndpointAdded, acmeWithEndpointAdded, \
    thriftWithEndpointAdded, walletCreatedForTestEnv, \
    faberInviteSyncedWithEndpoint, faberInviteSyncedWithoutEndpoint, \
    faberInviteLoadedByAlice, acceptInvitation, preRequisite

from sovrin_common.constants import ENDPOINT


@pytest.fixture(scope="module")
def faberMap(faberMapWithoutEndpointPubkey):
    fbrMap = faberMapWithoutEndpointPubkey
    endpointAttr = json.loads(fbrMap["endpointAttr"])
    base58Key = '5hmMA64DDQz5NzGJNVtRzNwpkZxktNQds21q3Wxxa62z'
    endpointAttr[ENDPOINT][PUBKEY] = base58Key
    fbrMap["endpointAttr"] = json.dumps(endpointAttr)
    return fbrMap


def testInvitationAcceptedIfAgentWasAddedUsingBase58AsPubkey(
        be, do, aliceCli, faberMap, preRequisite,
        syncedInviteAcceptedWithClaimsOut, faberInviteSyncedWithEndpoint):
    acceptInvitation(be, do, aliceCli, faberMap,
                     syncedInviteAcceptedWithClaimsOut)
