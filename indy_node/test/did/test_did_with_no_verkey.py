"""
Empty verkey tests
    Add a nym (16 byte, base58) without a verkey (Form 2).
        { type: NYM, dest: <id1> }
    Retrieve the verkey.
        { type: GET_NYM, dest: <id1> }
    Change verkey to new verkey (32 byte)
        { type: NYM, dest: <id1>, verkey: <vk1> }
    Retrieve new verkey
        { type: GET_NYM, dest: <id1> }
    Verify a signature from this identifier with the new verkey

DID Objects tests
    Store a DID object
    Retrieve a DID object
    Change a whole DID object
    Update just a portion of a DID object

DID forms tests
    Allow for identifiers that have the ‘did:indy:’ prefix
        did:indy:<16 byte, base58>
        Don’t store the prefix
    Allow for identifiers that omit the ‘did:indy:’ prefix
        <16 byte, base58>
    Allow for legacy cryptonyms
        Test that a 32-byte identifier is assumed to be a cryptonym, and the first 16 bytes are the identifier, and the last 16 bytes are the abbreviated verkey, and it is stored that way
    Any other forms are rejected.
"""

from stp_core.loop.eventually import eventually

from indy_common.identity import Identity
from indy_node.test.did.conftest import pf
from indy_node.test.did.helper import chkVerifyForRetrievedIdentity, \
    updateIndyIdrWithVerkey
from indy_client.test.helper import createNym
from plenum.test import waits as plenumWaits


@pf
def didAddedWithoutVerkey(
        addedTrustAnchor,
        looper,
        trustAnchor,
        trustAnchorWallet,
        wallet,
        noKeyIdr):
    """{ type: NYM, dest: <id1> }"""
    createNym(looper, noKeyIdr, trustAnchor, trustAnchorWallet)
    return wallet


@pf
def didUpdatedWithVerkey(didAddedWithoutVerkey, looper, trustAnchor,
                         trustAnchorWallet, noKeyIdr, wallet):
    """{ type: NYM, dest: <id1>, verkey: <vk1> }"""
    updateIndyIdrWithVerkey(looper, trustAnchorWallet, trustAnchor,
                            noKeyIdr, wallet.getVerkey(noKeyIdr))


@pf
def verkeyFetched(didUpdatedWithVerkey, looper, trustAnchor, trustAnchorWallet,
                  noKeyIdr, wallet):
    """{ type: GET_NYM, dest: <id1> }"""
    identity = Identity(identifier=noKeyIdr)
    req = trustAnchorWallet.requestIdentity(identity,
                                            sender=trustAnchorWallet.defaultId)
    trustAnchor.submitReqs(req)

    def chk():
        assert trustAnchorWallet.getIdentity(
            noKeyIdr).verkey == wallet.getVerkey(noKeyIdr)

    timeout = plenumWaits.expectedReqAckQuorumTime()
    looper.run(eventually(chk, retryWait=1, timeout=timeout))


def testWalletCanProvideAnIdentifierWithoutAKey(wallet, noKeyIdr):
    # TODO, Question: Why would `getVerkey` return `None` for a DID?.
    assert wallet.getVerkey(noKeyIdr)


def testAddDidWithoutAVerkey(didAddedWithoutVerkey):
    pass


def testRetrieveEmptyVerkey(didAddedWithoutVerkey, looper, trustAnchor,
                            trustAnchorWallet, noKeyIdr):
    """{ type: GET_NYM, dest: <id1> }"""
    identity = Identity(identifier=noKeyIdr)
    req = trustAnchorWallet.requestIdentity(identity,
                                            sender=trustAnchorWallet.defaultId)
    trustAnchor.submitReqs(req)

    def chk():
        assert trustAnchorWallet.getIdentity(noKeyIdr).verkey is None

    timeout = plenumWaits.expectedReqAckQuorumTime()
    looper.run(eventually(chk, retryWait=1, timeout=timeout))


def testChangeEmptyVerkeyToNewVerkey(didUpdatedWithVerkey):
    pass


def testRetrieveChangedVerkey(didUpdatedWithVerkey, verkeyFetched):
    pass


def testVerifySigWithChangedVerkey(didUpdatedWithVerkey, verkeyFetched,
                                   trustAnchorWallet, noKeyIdr, wallet):
    chkVerifyForRetrievedIdentity(wallet, trustAnchorWallet, noKeyIdr)
