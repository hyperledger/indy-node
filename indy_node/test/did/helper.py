import base58
from plenum.common.signer_did import DidSigner
from plenum.common.verifier import DidVerifier
from stp_core.loop.eventually import eventually
from plenum.test.helper import assertEquality
from plenum.test import waits as plenumWaits

from indy_common.identity import Identity

MsgForSigning = {'sender': 'Mario', 'msg': 'Lorem ipsum'}


def signMsg(wallet, idr):
    return wallet.signMsg(MsgForSigning, identifier=idr)


def verifyMsg(verifier, sig):
    sig = base58.b58decode(sig)
    return verifier.verifyMsg(sig, MsgForSigning)


def chkVerifyForRetrievedIdentity(signerWallet, verifierWallet, idr):
    sig = signMsg(signerWallet, idr)
    verkey = verifierWallet.getIdentity(idr).verkey
    assert verifyMsg(DidVerifier(verkey, idr), sig)


def updateWalletIdrWithFullKeySigner(wallet, idr):
    newSigner = DidSigner(identifier=idr)
    wallet.updateSigner(idr, newSigner)
    assertEquality(newSigner.verkey, wallet.getVerkey(idr))
    checkFullVerkeySize(wallet.getVerkey(idr))
    return newSigner.verkey


def updateWalletIdrWithFullVerkeySigner(wallet, idr, signer):
    wallet.updateSigner(idr, signer)
    assertEquality(signer.verkey, wallet.getVerkey(idr))
    checkFullVerkeySize(wallet.getVerkey(idr))


def updateIndyIdrWithVerkey(
        looper, senderWallet, senderClient, idr, fullKey):
    idy = Identity(identifier=idr, verkey=fullKey)
    senderWallet.updateTrustAnchoredIdentity(idy)
    # TODO: What if the request fails, there must be some rollback mechanism
    assert senderWallet.getTrustAnchoredIdentity(idr).seqNo is None
    reqs = senderWallet.preparePending()
    senderClient.submitReqs(*reqs)

    def chk():
        assert senderWallet.getTrustAnchoredIdentity(idr).seqNo is not None

    timeout = plenumWaits.expectedReqAckQuorumTime()
    looper.run(eventually(chk, retryWait=1, timeout=timeout))


def fetchFullVerkeyFromIndy(looper, senderWallet, senderClient,
                            ownerWallet, idr):
    identity = Identity(identifier=idr)
    req = senderWallet.requestIdentity(identity, sender=senderWallet.defaultId)
    senderClient.submitReqs(req)

    def chk():
        retrievedVerkey = senderWallet.getIdentity(idr).verkey
        assertEquality(retrievedVerkey, ownerWallet.getVerkey(idr))
        checkFullVerkeySize(retrievedVerkey)

    timeout = plenumWaits.expectedReqAckQuorumTime()
    looper.run(eventually(chk, retryWait=1, timeout=timeout))


def checkDidSize(did):
    # A base58 encoding of 32 bytes string can be either 44 bytes or 43 bytes,
    # since the did takes first 16 bytes, base58 of did is either
    # 21 or 22 characters
    assert len(did) == 21 or len(did) == 22


def checkAbbrVerkeySize(verkey):
    # A base58 encoding of 32 bytes string can be either 44 bytes or 43 bytes,
    # since the abbreviated verkey takes last 16 bytes, base58 of abbreviated
    # verkey is either 21 or 22 characters and since its prefixed by a `~` its
    # length will be either 23 or 22
    assert len(verkey) == 23 or len(verkey) == 22


def checkFullVerkeySize(verkey):
    # A base58 encoding of 32 bytes string can be either 44 bytes or 43 bytes.
    assert len(verkey) == 44 or len(verkey) == 43
