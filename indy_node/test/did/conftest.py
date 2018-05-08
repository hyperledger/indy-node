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
def client(wallet, looper, tdirWithClientPoolTxns):
    s, _ = genTestClient(tmpdir=tdirWithClientPoolTxns, usePoolLedger=True)
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
    idr = base58.b58encode(b'1' * 16).decode("utf-8")
    return wallet.addIdentifier(identifier=idr)[0]


@pf
def fullKeyIdr(wallet):
    idr = base58.b58encode(b'2' * 16).decode("utf-8")
    return wallet.addIdentifier(identifier=idr)[0]
