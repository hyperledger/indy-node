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

import base58
import pytest

from indy_client.client.wallet.wallet import Wallet
from indy_node.test.helper import makePendingTxnsRequest
from indy_client.test.helper import genTestClient

pf = pytest.fixture(scope='module')


@pf
def wallet():
    return Wallet('my wallet')


@pf
def client(wallet, looper, tdir):
    s, _ = genTestClient(tmpdir=tdir, usePoolLedger=True)
    s.registerObserver(wallet.handleIncomingReply)
    looper.add(s)
    looper.run(s.ensureConnectedToNodes())
    makePendingTxnsRequest(s, wallet)
    return s


@pf
def abbrevIdr(wallet):
    idr, _ = wallet.addIdentifier()
    return idr


@pf
def abbrevVerkey(wallet, abbrevIdr):
    return wallet.getVerkey(abbrevIdr)


@pf
def noKeyIdr(wallet):
    idr = base58.b58encode(b'1' * 16)
    return wallet.addIdentifier(identifier=idr)[0]


@pf
def fullKeyIdr(wallet):
    idr = base58.b58encode(b'2' * 16)
    return wallet.addIdentifier(identifier=idr)[0]
