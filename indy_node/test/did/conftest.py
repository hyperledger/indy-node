import json

import base58
import pytest

from indy.did import create_and_store_my_did
from indy_client.client.wallet.wallet import Wallet
from indy_node.test.helper import makePendingTxnsRequest
from indy_client.test.helper import genTestClient
from plenum.common.util import randomString

pf = pytest.fixture(scope='module')


@pf
def wallet():
    return Wallet('my wallet')


@pf
def client(wallet, looper, tdirWithClientPoolTxns):
    s, _ = genTestClient(tmpdir=tdirWithClientPoolTxns, usePoolLedger=True)
    s.registerObserver(wallet.handleIncomingReply)
    looper.add(s)
    looper.run(s.ensureConnectedToNodes())
    makePendingTxnsRequest(s, wallet)
    return s


@pf
def wh(sdk_wallet_client):
    wh, _ = sdk_wallet_client
    return wh


@pf
def abbrevIdr(looper, wh):
    seed = randomString(32)
    did, _ = looper.loop.run_until_complete(
        create_and_store_my_did(wh, json.dumps({'seed': seed, 'cid': True})))
    return did


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
