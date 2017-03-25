"""
Abbreviated verkey tests
    Add a nym (16 byte, base58) with an abbreviated verkey (‘~’ with 16 bytes, base58) (Form 3)
        { type: NYM, dest: <id3>, verkey: ~<16byte abbreviated key> }
    Retrieve the verkey.
        { type: GET_NYM, dest: <id3> }
    Verify a signature from this identifier
    Change a verkey for a nym with a full verkey.
        { type: NYM, dest: <id3>, verkey: <32byte ED25519 key> }
    Retrieve new verkey
        { type: GET_NYM, dest: <id3> }
    Verify a signature from this identifier with the new verkey
"""
from plenum.common.signer_did import DidSigner
from stp_core.loop.eventually import eventually
from plenum.test.helper import assertLength, assertEquality

from sovrin_common.identity import Identity
from sovrin_node.test.did.conftest import pf
from sovrin_node.test.did.helper import chkVerifyForRetrievedIdentity, \
    updateWalletIdrWithFullKeySigner, updateSovrinIdrWithFullKey, \
    fetchFullVerkeyFromSovrin, checkAbbrVerkeySize, checkDidSize, \
    updateWalletIdrWithFullVerkeySigner
from sovrin_client.test.helper import createNym


@pf
def didAddedWithAbbrvVerkey(addedSponsor, looper, sponsor, sponsorWallet,
                          wallet, abbrevIdr):
    """{ type: NYM, dest: <id1> }"""
    createNym(looper, abbrevIdr, sponsor, sponsorWallet,
              verkey=wallet.getVerkey(abbrevIdr))
    return wallet


@pf
def newAbbrvKey(wallet, abbrevIdr):
    newSigner = DidSigner(identifier=abbrevIdr)
    wallet.updateSigner(abbrevIdr, newSigner)
    assertEquality(newSigner.verkey, wallet.getVerkey(abbrevIdr))
    return newSigner.verkey


@pf
def newFullKeySigner(wallet, abbrevIdr):
    return DidSigner(identifier=abbrevIdr)


@pf
def newFullKey(newFullKeySigner):
    return newFullKeySigner.verkey


@pf
def didUpdatedWithFullVerkey(didAddedWithAbbrvVerkey, looper, sponsor,
                            sponsorWallet, abbrevIdr, newFullKey,
                             newFullKeySigner, wallet, client):
    """{ type: NYM, dest: <id1>, verkey: <vk1> }"""
    # updateSovrinIdrWithFullKey(looper, sponsorWallet, sponsor, wallet,
    #                            abbrevIdr, newFullKey)
    updateSovrinIdrWithFullKey(looper, wallet, client, wallet,
                               abbrevIdr, newFullKey)
    updateWalletIdrWithFullVerkeySigner(wallet, abbrevIdr, newFullKeySigner)


@pf
def newVerkeyFetched(didAddedWithAbbrvVerkey, looper, sponsor, sponsorWallet,
                     abbrevIdr, wallet):
    """{ type: GET_NYM, dest: <id1> }"""
    fetchFullVerkeyFromSovrin(looper, sponsorWallet, sponsor, wallet,
                              abbrevIdr)


def testNewIdentifierInWalletIsDid(abbrevIdr):
    checkDidSize(abbrevIdr)


def testDefaultVerkeyIsAbbreviated(abbrevVerkey):
    # A base58 encoding of 32 bytes string can be either 44 bytes or 43 bytes,
    # since the did takes first 22 bytes,  abbreviated verkey will take
    # remaining 22 or 21 characters
    checkAbbrVerkeySize(abbrevVerkey)
    assert abbrevVerkey[0] == '~'


def testAddDidWithVerkey(didAddedWithAbbrvVerkey):
    pass


def testRetrieveAbbrvVerkey(didAddedWithAbbrvVerkey, looper, sponsor,
                            sponsorWallet, wallet, abbrevIdr):
    """{ type: GET_NYM, dest: <id1> }"""
    identity = Identity(identifier=abbrevIdr)
    req = sponsorWallet.requestIdentity(identity,
                                        sender=sponsorWallet.defaultId)
    sponsor.submitReqs(req)

    def chk():
        retrievedVerkey = sponsorWallet.getIdentity(abbrevIdr).verkey
        assertEquality(retrievedVerkey, wallet.getVerkey(abbrevIdr))
        checkAbbrVerkeySize(retrievedVerkey)
    looper.run(eventually(chk, retryWait=1, timeout=5))
    chkVerifyForRetrievedIdentity(wallet, sponsorWallet, abbrevIdr)


def testChangeVerkeyToNewVerkey(didUpdatedWithFullVerkey):
    pass


def testRetrieveChangedVerkey(didUpdatedWithFullVerkey, newVerkeyFetched):
    pass


def testVerifySigWithChangedVerkey(didUpdatedWithFullVerkey, newVerkeyFetched,
                                   sponsorWallet, abbrevIdr, wallet):
    chkVerifyForRetrievedIdentity(wallet, sponsorWallet, abbrevIdr)
