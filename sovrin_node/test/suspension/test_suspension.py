import pytest

from sovrin_node.test.suspension.helper import sendChangeVerkey, checkIdentityRequestFailed, \
    checkIdentityRequestSucceed, sendSuspendRole, changeVerkey, suspendRole
from stp_core.loop.eventually import eventually
from plenum.common.constants import TRUSTEE, STEWARD
from plenum.common.util import randomString, hexToFriendly
from plenum.test.pool_transactions.helper import suspendNode
from plenum.test.pool_transactions.test_suspend_node import \
    checkNodeNotInNodeReg
from sovrin_client.test.helper import addRole, \
    getClientAddedWithRole
from sovrin_common.constants import TGB, TRUST_ANCHOR

whitelist = ['Observer threw an exception', 'while verifying message']


@pytest.fixture(scope="module")
def anotherTrustee(nodeSet, tdir, looper, trustee, trusteeWallet):
    return getClientAddedWithRole(nodeSet, tdir, looper,
                                  trustee, trusteeWallet, 'newTrustee', TRUSTEE)


@pytest.fixture(scope="module")
def anotherTGB(nodeSet, tdir, looper, trustee, trusteeWallet):
    return getClientAddedWithRole(nodeSet, tdir, looper,
                                  trustee, trusteeWallet, 'newTGB', TGB)


@pytest.fixture(scope="module")
def anotherSteward(nodeSet, tdir, looper, trustee, trusteeWallet):
    return getClientAddedWithRole(nodeSet, tdir, looper,
                                  trustee, trusteeWallet, 'newSteward', STEWARD)


@pytest.fixture(scope="module")
def anotherSteward1(nodeSet, tdir, looper, trustee, trusteeWallet):
    return getClientAddedWithRole(nodeSet, tdir, looper,
                                  trustee, trusteeWallet, 'newSteward1', STEWARD)


@pytest.fixture(scope="module")
def anotherTrustAnchor(nodeSet, tdir, looper, trustee, trusteeWallet):
    return getClientAddedWithRole(nodeSet, tdir, looper,
                                  trustee, trusteeWallet, 'newTrustAnchor', TRUST_ANCHOR)


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
        addRole(looper, *anotherSteward, name=randomString(), role=TRUST_ANCHOR)


def testTrustAnchorSuspensionByTrustee(looper, anotherTrustee, anotherTrustAnchor):
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
    for identity in (anotherTrustee, anotherTGB, anotherSteward, anotherTrustAnchor):
        # Trustee cannot change verkey
        _, wallet = identity
        changeVerkey(looper, trustee, trusteeWallet, wallet.defaultId, '',
                     nAckReasonContains='cannot update verkey')
        # Owner can change verkey
        changeVerkey(looper, *identity, wallet.defaultId, '')


# The test suspends a node, this action affects on other tests.
# The test has to be the last in this module. It is not a good way.
# TODO testValidatorSuspensionByTrustee should not affect on other tests
def testValidatorSuspensionByTrustee(trustee, trusteeWallet, looper, nodeSet):
    node = nodeSet[-1]
    nodeNym = hexToFriendly(node.nodestack.verhex)
    suspendNode(looper, trustee, trusteeWallet, nodeNym, node.name)
    for n in nodeSet[:-1]:
        looper.run(eventually(checkNodeNotInNodeReg, n, node.name))
    looper.run(eventually(checkNodeNotInNodeReg, trustee, node.name))