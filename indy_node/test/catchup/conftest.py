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

import pytest

from indy_client.test.helper import getClientAddedWithRole
from indy_node.test.did.helper import updateIndyIdrWithVerkey


@pytest.fixture(scope="module")
def some_transactions_done(looper, nodeSet, tdirWithPoolTxns, trustee,
                           trusteeWallet):
    new_c, new_w = getClientAddedWithRole(nodeSet, tdirWithPoolTxns, looper,
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
