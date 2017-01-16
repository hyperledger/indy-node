import base58
import pytest

from sovrin_client.client.wallet.wallet import Wallet

pf = pytest.fixture(scope='module')


@pf
def wallet():
    return Wallet('my wallet')


@pf
def abbrevIdr(wallet):
    idr, _ = wallet.addIdentifier()
    return idr


@pf
def abbrevVerkey(wallet, abbrevIdr):
    return wallet.getVerkey(abbrevIdr)


@pf
def noKeyIdr(wallet):
    idr = base58.b58encode(b'1'*16)
    return wallet.addIdentifier(identifier=idr)[0]


@pf
def fullKeyIdr(wallet):
    idr = base58.b58encode(b'2'*16)
    return wallet.addIdentifier(identifier=idr)[0]
