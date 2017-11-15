import json

import pytest

from plenum.common.constants import PUBKEY

# noinspection PyUnresolvedReferences
from indy_client.test.cli.conftest \
    import faberMap as faberMapWithoutEndpointPubkey

# noinspection PyUnresolvedReferences
from indy_client.test.cli.test_tutorial import alice_accepted_faber_request, \
    aliceCli, preRequisite, faberCli, acmeCli, thriftCli, faberWithEndpointAdded, acmeWithEndpointAdded, \
    thriftWithEndpointAdded, walletCreatedForTestEnv, \
    faberInviteSyncedWithEndpoint, faberInviteSyncedWithoutEndpoint, \
    faberInviteLoadedByAlice, accept_request, preRequisite

from indy_common.constants import ENDPOINT


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
    accept_request(be, do, aliceCli, faberMap,
                   syncedInviteAcceptedWithClaimsOut)
