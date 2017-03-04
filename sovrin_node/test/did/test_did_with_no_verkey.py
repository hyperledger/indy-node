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
    Allow for identifiers that have the ‘did:sovrin:’ prefix
        did:sovrin:<16 byte, base58>
        Don’t store the prefix
    Allow for identifiers that omit the ‘did:sovrin:’ prefix
        <16 byte, base58>
    Allow for legacy cryptonyms
        Test that a 32-byte identifier is assumed to be a cryptonym, and the first 16 bytes are the identifier, and the last 16 bytes are the abbreviated verkey, and it is stored that way
    Any other forms are rejected.
"""

from plenum.common.eventually import eventually

from sovrin_common.identity import Identity
from sovrin_node.test.did.conftest import pf
from sovrin_node.test.did.helper import chkVerifyForRetrievedIdentity, \
    updateSovrinIdrWithFullKey
from sovrin_client.test.helper import createNym


@pf
def didAddedWithoutVerkey(addedSponsor, looper, sponsor, sponsorWallet,
                          wallet, noKeyIdr):
    """{ type: NYM, dest: <id1> }"""
    createNym(looper, noKeyIdr, sponsor, sponsorWallet)
    return wallet

@pf
def didUpdatedWithVerkey(didAddedWithoutVerkey, looper, sponsor,
                            sponsorWallet, noKeyIdr, wallet):
    """{ type: NYM, dest: <id1>, verkey: <vk1> }"""
    updateSovrinIdrWithFullKey(looper, sponsorWallet, sponsor, wallet,
                               noKeyIdr, wallet.getVerkey(noKeyIdr))


@pf
def verkeyFetched(didUpdatedWithVerkey, looper, sponsor, sponsorWallet,
                  noKeyIdr, wallet):
    """{ type: GET_NYM, dest: <id1> }"""
    identity = Identity(identifier=noKeyIdr)
    req = sponsorWallet.requestIdentity(identity,
                                        sender=sponsorWallet.defaultId)
    sponsor.submitReqs(req)

    def chk():
        assert sponsorWallet.getIdentity(noKeyIdr).verkey == wallet.getVerkey(
            noKeyIdr)

    looper.run(eventually(chk, retryWait=1, timeout=5))


def testWalletCanProvideAnIdentifierWithoutAKey(wallet, noKeyIdr):
    # TODO, Question: Why would `getVerkey` return `None` for a DID?.
    assert wallet.getVerkey(noKeyIdr)


def testAddDidWithoutAVerkey(didAddedWithoutVerkey):
    pass


def testRetrieveEmptyVerkey(didAddedWithoutVerkey, looper, sponsor,
                            sponsorWallet, noKeyIdr):
    """{ type: GET_NYM, dest: <id1> }"""
    identity = Identity(identifier=noKeyIdr)
    req = sponsorWallet.requestIdentity(identity, sender=sponsorWallet.defaultId)
    sponsor.submitReqs(req)

    def chk():
        assert sponsorWallet.getIdentity(noKeyIdr).verkey is None

    looper.run(eventually(chk, retryWait=1, timeout=5))


def testChangeEmptyVerkeyToNewVerkey(didUpdatedWithVerkey):
    pass


def testRetrieveChangedVerkey(didUpdatedWithVerkey, verkeyFetched):
    pass


def testVerifySigWithChangedVerkey(didUpdatedWithVerkey, verkeyFetched,
                                   sponsorWallet, noKeyIdr, wallet):
    chkVerifyForRetrievedIdentity(wallet, sponsorWallet, noKeyIdr)
