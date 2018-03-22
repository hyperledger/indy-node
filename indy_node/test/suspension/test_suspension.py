import pytest

from plenum.common.signer_did import DidSigner
from indy_node.test.suspension.helper import sendChangeVerkey, checkIdentityRequestFailed, \
    checkIdentityRequestSucceed, sendSuspendRole, changeVerkey, suspendRole
from stp_core.loop.eventually import eventually
from stp_core.common.log import getlogger
from plenum.common.constants import TRUSTEE, STEWARD
from plenum.common.util import randomString, hexToFriendly
from plenum.test.pool_transactions.helper import suspendNode
from plenum.test.pool_transactions.test_suspend_node import \
    checkNodeNotInNodeReg
from indy_client.test.helper import addRole, \
    getClientAddedWithRole
from indy_common.constants import TGB, TRUST_ANCHOR

whitelist = ['Observer threw an exception', 'while verifying message']


logger = getlogger()


@pytest.fixture(scope="module")
def anotherTrustee(nodeSet, tdirWithClientPoolTxns, looper, trustee, trusteeWallet):
    return getClientAddedWithRole(nodeSet, tdirWithClientPoolTxns, looper,
                                  trustee, trusteeWallet, 'newTrustee',
                                  role=TRUSTEE)


@pytest.fixture(scope="module")
def anotherTGB(nodeSet, tdirWithClientPoolTxns, looper, trustee, trusteeWallet):
    return getClientAddedWithRole(nodeSet, tdirWithClientPoolTxns, looper,
                                  trustee, trusteeWallet, 'newTGB', role=TGB)


@pytest.fixture(scope="module")
def anotherSteward(nodeSet, tdirWithClientPoolTxns, looper, trustee, trusteeWallet):
    return getClientAddedWithRole(nodeSet, tdirWithClientPoolTxns, looper,
                                  trustee, trusteeWallet, 'newSteward',
                                  role=STEWARD)


@pytest.fixture(scope="module")
def anotherSteward1(nodeSet, tdirWithClientPoolTxns, looper, trustee, trusteeWallet):
    return getClientAddedWithRole(nodeSet, tdirWithClientPoolTxns, looper,
                                  trustee, trusteeWallet, 'newSteward1',
                                  role=STEWARD)


@pytest.fixture(scope="module")
def anotherTrustAnchor(nodeSet, tdirWithClientPoolTxns, looper, trustee, trusteeWallet):
    return getClientAddedWithRole(nodeSet, tdirWithClientPoolTxns, looper,
                                  trustee, trusteeWallet, 'newTrustAnchor',
                                  role=TRUST_ANCHOR)


@pytest.fixture(scope="module")
def anotherTrustAnchor1(nodeSet, tdirWithClientPoolTxns, looper, trustee, trusteeWallet):
    return getClientAddedWithRole(nodeSet, tdirWithClientPoolTxns, looper,
                                  trustee, trusteeWallet, 'newTrustAnchor1',
                                  role=TRUST_ANCHOR)


def testTrusteeAddingAnotherTrustee(anotherTrustee):
    pass


def testTrusteeAddingTGB(looper, anotherTGB):
    # The new TGB adds a NYM
    addRole(looper, *anotherTGB, name=randomString())


def testTrusteeAddingSteward(looper, anotherSteward):
    # The new Steward adds a TRUST_ANCHOR
    addRole(looper, *anotherSteward, name=randomString(), role=TRUST_ANCHOR)


def testTrusteeAddingTrustAnchor(looper, anotherTrustAnchor):
    # The new TTrustAnchor adds a NYM
    addRole(looper, *anotherTrustAnchor, name=randomString())


def testTGBSuspensionByTrustee(looper, anotherTrustee, anotherTGB):
    trClient, trWallet = anotherTrustee
    _, tgbWallet = anotherTGB
    suspendRole(looper, trClient, trWallet, tgbWallet.defaultId)
    with pytest.raises(AssertionError):
        addRole(looper, *anotherTGB, name=randomString())


def testStewardSuspensionByTrustee(looper, anotherTrustee, anotherSteward):
    trClient, trWallet = anotherTrustee
    _, stWallet = anotherSteward
    suspendRole(looper, trClient, trWallet, stWallet.defaultId)
    with pytest.raises(AssertionError):
        addRole(looper, *anotherSteward,
                name=randomString(), role=TRUST_ANCHOR)


def testTrustAnchorSuspensionByTrustee(
        looper, anotherTrustee, anotherTrustAnchor):
    trClient, trWallet = anotherTrustee
    _, spWallet = anotherTrustAnchor
    suspendRole(looper, trClient, trWallet, spWallet.defaultId)
    with pytest.raises(AssertionError):
        addRole(looper, *anotherTrustAnchor, name=randomString())


def testTrusteeSuspensionByTrustee(looper, trustee, trusteeWallet,
                                   anotherTrustee, anotherSteward1):
    # trustee suspension by trustee is succeed
    trClient, trWallet = anotherTrustee
    suspendRole(looper, trustee, trusteeWallet, trWallet.defaultId)

    # trustee suspension by steward1 is failed
    _, sWallet = anotherSteward1
    suspendRole(looper, trClient, trWallet, sWallet.defaultId,
                nAckReasonContains='is neither Trustee nor owner of')


def testTrusteeCannotChangeVerkey(trustee, trusteeWallet, looper, nodeSet,
                                  anotherTrustee, anotherTGB, anotherSteward,
                                  anotherTrustAnchor):
    for identity in (anotherTrustee, anotherTGB, anotherSteward,
                     anotherTrustAnchor):
        # Trustee cannot change verkey
        _, wallet = identity
        signer = DidSigner()
        changeVerkey(looper, trustee, trusteeWallet, wallet.defaultId,
                     signer.verkey,
                     nAckReasonContains='TRUSTEE cannot update verkey')
        # Identity owner can change verkey
        changeVerkey(looper, *identity, wallet.defaultId, signer.verkey)


def testTrustAnchorSuspendingHimselfByVerkeyFlush(looper, trustee, trusteeWallet, anotherTrustAnchor1):
    _, wallet = anotherTrustAnchor1
    changeVerkey(looper, *anotherTrustAnchor1, wallet.defaultId, '')
    signer = DidSigner()
    changeVerkey(looper, *anotherTrustAnchor1, wallet.defaultId, signer.verkey,
                 nAckReasonContains="CouldNotAuthenticate('Can not find verkey for")
    # Now NYM creator should have permission to set verkey.
    changeVerkey(looper, trustee, trusteeWallet, wallet.defaultId, signer.verkey)


# Keep the test below at the end of the suite since it will make one of the
# nodes inactive, unless you are planning to add new nodes.
def testValidatorSuspensionByTrustee(trustee, trusteeWallet, looper, nodeSet):
    node = nodeSet[-1]
    nodeNym = hexToFriendly(node.nodestack.verhex)
    suspendNode(looper, trustee, trusteeWallet, nodeNym, node.name)
    for n in nodeSet[:-1]:
        looper.run(eventually(checkNodeNotInNodeReg, n, node.name))
    looper.run(eventually(checkNodeNotInNodeReg, trustee, node.name))
