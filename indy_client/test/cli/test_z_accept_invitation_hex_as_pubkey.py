#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import json

import pytest

from plenum.common.constants import PUBKEY
from plenum.common.exceptions import BlowUp
from plenum.common.util import cryptonymToHex

# noinspection PyUnresolvedReferences
from indy_client.test.cli.conftest \
    import faberMap as faberMapWithoutEndpointPubkey

# noinspection PyUnresolvedReferences
from indy_client.test.cli.test_tutorial import alice_accepted_faber_request, \
    aliceCli, preRequisite, faberCli, acmeCli, thriftCli, faberWithEndpointAdded, acmeWithEndpointAdded, \
    thriftWithEndpointAdded, walletCreatedForTestEnv, \
    faberInviteSyncedWithEndpoint, faberInviteSyncedWithoutEndpoint, \
    faberInviteLoadedByAlice, accept_request

from indy_common.constants import ENDPOINT


@pytest.fixture(scope="module")
def faberMap(faberMapWithoutEndpointPubkey):
    fbrMap = faberMapWithoutEndpointPubkey
    endpointAttr = json.loads(fbrMap["endpointAttr"])
    base58Key = '5hmMA64DDQz5NzGJNVtRzNwpkZxktNQds21q3Wxxa62z'
    hexKey = cryptonymToHex(base58Key).decode()
    endpointAttr[ENDPOINT][PUBKEY] = hexKey
    fbrMap["endpointAttr"] = json.dumps(endpointAttr)
    return fbrMap


def test_request_not_accepted_if_agent_was_added_using_hex_as_pubkey(
        be, do, aliceCli, faberMap, preRequisite,
        syncedInviteAcceptedWithClaimsOut, faberInviteSyncedWithEndpoint):
    with pytest.raises(BlowUp):
        accept_request(be, do, aliceCli, faberMap,
                       syncedInviteAcceptedWithClaimsOut)
