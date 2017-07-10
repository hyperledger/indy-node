import pytest
from plenum.common.signer_did import DidSigner
from plenum.common.signer_simple import SimpleSigner
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.test.cli.helper import prompt_is, addNym, ensureConnectedToTestEnv
from sovrin_common.roles import Roles
from sovrin_node.test.did.conftest import wallet, abbrevVerkey

TRUST_ANCHOR_SEED = b'TRUST0NO0ONE00000000000000000000'


@pytest.fixture("module")
def trust_anchor_did_signer():
    return DidSigner(seed=TRUST_ANCHOR_SEED)


@pytest.fixture("module")
def trust_anchor_cid_signer():
    return SimpleSigner(seed=TRUST_ANCHOR_SEED)


@pytest.fixture("module")
def trustAnchorWallet(trustAnchorSigner):
    w = Wallet(trustAnchorSigner.identifier)
    w.addIdentifier(signer=trustAnchorSigner)
    return w


def testPoolNodesStarted(poolNodesStarted):
    pass


@pytest.fixture(scope="module")
def aliceCli(be, do, poolNodesStarted, aliceCLI, connectedToTest, wallet):
    be(aliceCLI)
    do('prompt Alice', expect=prompt_is('Alice'))
    addAndActivateCLIWallet(aliceCLI, wallet)
    do('connect test', within=3, expect=connectedToTest)
    return aliceCLI


@pytest.fixture(scope="module")
def trustAnchorCli(be, do, poolNodesStarted, earlCLI, connectedToTest,
               trustAnchorWallet):
    be(earlCLI)
    do('prompt Earl', expect=prompt_is('Earl'))
    addAndActivateCLIWallet(earlCLI, trustAnchorWallet)
    do('connect test', within=3, expect=connectedToTest)
    return earlCLI


def getNym(be, do, userCli, idr, expectedMsgs):
    be(userCli)
    do('send GET_NYM dest={}'.format(idr),
       within=3,
       expect=expectedMsgs
       )


def getNymNotFoundExpectedMsgs(idr):
    return ["NYM {} not found".format(idr)]


def testGetDIDWithoutAddingIt(be, do, philCli, trust_anchor_did_signer):
    ensureConnectedToTestEnv(be, do, philCli)
    getNym(be, do, philCli, trust_anchor_did_signer.identifier,
           getNymNotFoundExpectedMsgs(trust_anchor_did_signer.identifier))


def testGetCIDWithoutAddingIt(be, do, philCli, trust_anchor_cid_signer):
    ensureConnectedToTestEnv(be, do, philCli)
    getNym(be, do, philCli, trust_anchor_cid_signer.identifier,
           getNymNotFoundExpectedMsgs(trust_anchor_cid_signer.identifier))


def addAndActivateCLIWallet(cli, wallet):
    cli.wallets[wallet.name] = wallet
    cli.activeWallet = wallet


@pytest.fixture(scope="module")
def didAdded(be, do, philCli, trust_anchor_did_signer):
    ensureConnectedToTestEnv(be, do, philCli)
    addNym(be, do, philCli,
           trust_anchor_did_signer.identifier,
           role=Roles.TRUST_ANCHOR.name
           )
    return philCli


def testAddDID(didAdded):
    pass


@pytest.fixture(scope="module")
def cidAdded(be, do, philCli, trust_anchor_cid_signer):
    addNym(be, do, philCli, trust_anchor_cid_signer.identifier, role=Roles.TRUST_ANCHOR.name)
    return philCli


def testAddCID(cidAdded):
    pass


def getNoVerkeyEverAssignedMsgs(idr):
    return ["No verkey ever assigned to the identifier {}".format(idr)]


def testGetDIDWithoutVerkey(be, do, philCli, didAdded, trust_anchor_did_signer):
    getNym(be, do, philCli, trust_anchor_did_signer.identifier,
           getNoVerkeyEverAssignedMsgs(trust_anchor_did_signer.identifier))


def getVerkeyIsSameAsIdentifierMsgs(idr):
    return ["Current verkey is same as identifier {}".format(idr)]


def testGetCIDWithoutVerkey(be, do, philCli, cidAdded, trust_anchor_cid_signer):
    getNym(be, do, philCli, trust_anchor_cid_signer.identifier,
           getVerkeyIsSameAsIdentifierMsgs(trust_anchor_cid_signer.identifier))


@pytest.fixture(scope="module")
def verkeyAddedToDID(be, do, philCli, didAdded, trust_anchor_did_signer):
    addNym(be, do, philCli, trust_anchor_did_signer.identifier,
           trust_anchor_did_signer.verkey)


def testAddVerkeyToExistingDID(verkeyAddedToDID):
    pass


@pytest.fixture(scope="module")
def verkeyAddedToCID(be, do, philCli, cidAdded, trust_anchor_cid_signer):
    # newSigner = SimpleSigner(identifier=trust_anchor_cid_signer.identifier)
    # new_verkey = newSigner.verkey

    addNym(be, do, philCli, trust_anchor_cid_signer.identifier, verkey=trust_anchor_cid_signer.verkey)
    return trust_anchor_cid_signer


def testAddVerkeyToExistingCID(verkeyAddedToCID):
    pass


def getCurrentVerkeyIsgMsgs(idr, verkey):
    return ["Current verkey for NYM {} is {}".format(idr, verkey)]


def testGetDIDWithVerKey(be, do, philCli, verkeyAddedToDID,
                         trust_anchor_did_signer):
    getNym(be, do, philCli, trust_anchor_did_signer.identifier,
           getCurrentVerkeyIsgMsgs(trust_anchor_did_signer.identifier,
                                   trust_anchor_did_signer.verkey))


def testGetCIDWithVerKey(be, do, philCli, verkeyAddedToCID,
                         trust_anchor_cid_signer):
    getNym(be, do, philCli, trust_anchor_cid_signer.identifier,
           getCurrentVerkeyIsgMsgs(trust_anchor_cid_signer.identifier,
                                   trust_anchor_cid_signer.verkey))


def getNoActiveVerkeyFoundMsgs(idr):
    return ["No active verkey found for the identifier {}".format(idr)]


def addAttribToNym(be, do, userCli, idr, raw):
    be(userCli)
    do('send ATTRIB dest={} raw={}'.format(idr, raw),
       within=5,
       expect=["Attribute added for nym {}".format(idr)])

@pytest.mark.skip("INDY- This should not have worked")
def testSendAttribForDID(be, do, verkeyAddedToDID, trust_anchor_did_signer, aliceCli):
    raw = '{"name": "Alice"}'
    addAttribToNym(be, do, aliceCli, trust_anchor_did_signer.identifier, raw)

@pytest.mark.skip("INDY- This should not have worked")
def testSendAttribForCID(be, do, verkeyAddedToCID, trust_anchor_cid_signer, trustAnchorCli):
    raw = '{"name": "Earl"}'
    addAttribToNym(be, do, trustAnchorCli, trust_anchor_cid_signer.identifier, raw)


@pytest.fixture(scope="module")
def verkeyRemovedFromExistingDID(be, do, verkeyAddedToDID, abbrevIdr, aliceCli):
    be(aliceCli)
    addNym(be, do, aliceCli, abbrevIdr, '')
    getNym(be, do, aliceCli, abbrevIdr, getNoActiveVerkeyFoundMsgs(abbrevIdr))


@pytest.mark.skip(reason="verkey removal is not supported")
def testRemoveVerkeyFromDID(verkeyRemovedFromExistingDID):
    pass


@pytest.fixture(scope="module")
def verkeyRemovedFromExistingCID(be, do, verkeyAddedToCID,
                                 trustAnchorSigner, trustAnchorCli, trustAnchorWallet):
    be(trustAnchorCli)
    addNym(be, do, trustAnchorCli, trustAnchorSigner.identifier, '')
    getNym(be, do, trustAnchorCli, trustAnchorSigner.identifier,
           getNoActiveVerkeyFoundMsgs(trustAnchorSigner.identifier))


@pytest.mark.skip(reason="verkey removal is not supported")
def testRemoveVerkeyFromCID(verkeyRemovedFromExistingCID):
    pass


@pytest.mark.skip(reason="SOV-568. Obsolete assumption, if an identity has set "
                         "its verkey to blank, no-one including "
                         "itself can change it")
def testNewverkeyAddedToDID(be, do, philCli, abbrevIdr,
                            verkeyRemovedFromExistingDID):
    newSigner = DidSigner()
    addNym(be, do, philCli, abbrevIdr, newSigner.verkey)
    getNym(be, do, philCli, abbrevIdr,
           getCurrentVerkeyIsgMsgs(abbrevIdr, newSigner.verkey))


@pytest.mark.skip(reason="SOV-568. Obsolete assumption, if an identity has set "
                         "its verkey to blank, no-one including "
                         "itself can change it")
def testNewverkeyAddedToCID(be, do, philCli, trustAnchorSigner,
                            verkeyRemovedFromExistingCID):
    newSigner = DidSigner()
    addNym(be, do, philCli, trustAnchorSigner.identifier, newSigner.verkey)
    getNym(be, do, philCli, trustAnchorSigner.identifier,
           getCurrentVerkeyIsgMsgs(trustAnchorSigner.identifier, newSigner.verkey))


def testNewKeyChangesWalletsDefaultId(be, do, poolNodesStarted,
                                      susanCLI, connectedToTest):
    mywallet = Wallet('my wallet')
    keyseed = 'a' * 32
    idr, _ = mywallet.addIdentifier(seed=keyseed.encode("utf-8"))

    be(susanCLI)

    do('connect test', within=3, expect=connectedToTest)

    do('new key with seed {}'.format(keyseed))

    do('send NYM dest={}'.format(idr))

    do('new key with seed 11111111111111111111111111111111')

    do('send NYM dest={}'.format(idr), within=3,
       expect=["Nym {} added".format(idr)])




