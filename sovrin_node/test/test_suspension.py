import pytest

from plenum.common.eventually import eventually
from plenum.common.util import randomString, hexToFriendly
from plenum.test.pool_transactions.helper import suspendNode
from plenum.test.pool_transactions.test_suspend_node import \
    checkNodeNotInNodeReg
from sovrin_common.txn import STEWARD, TGB
from sovrin_common.txn import TRUSTEE, SPONSOR
from sovrin_client.test.helper import addRole, suspendRole, \
    getClientAddedWithRole, changeVerkey

whitelist = ['Observer threw an exception']


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
def anotherSponsor(nodeSet, tdir, looper, trustee, trusteeWallet):
    return getClientAddedWithRole(nodeSet, tdir, looper,
                                  trustee, trusteeWallet, 'newSponsor', SPONSOR)


def testTrusteeAddingAnotherTrustee(anotherTrustee):
    pass


def testTrusteeAddingTGB(looper, anotherTGB):
    # The new TGB adds a NYM
    addRole(looper, *anotherTGB, name=randomString())


def testTrusteeAddingSteward(looper, anotherSteward):
    # The new Steward adds a SPONSOR
    addRole(looper, *anotherSteward, name=randomString(), role=SPONSOR)


def testTrusteeAddingSponsor(looper, anotherSponsor):
    # The new TSponsor adds a NYM
    addRole(looper, *anotherSponsor, name=randomString())


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
        addRole(looper, *anotherSteward, name=randomString(), role=SPONSOR)


def testSponsorSuspensionByTrustee(looper, anotherTrustee, anotherSponsor):
    trClient, trWallet = anotherTrustee
    _, spWallet = anotherSponsor
    suspendRole(looper, trClient, trWallet, spWallet.defaultId)
    with pytest.raises(AssertionError):
        addRole(looper, *anotherSponsor, name=randomString())


def testTrusteeSuspensionByTrustee(looper, trustee, trusteeWallet,
                                   anotherTrustee):
    _, trWallet = anotherTrustee
    suspendRole(looper, trustee, trusteeWallet, trWallet.defaultId)


def testValidatorSuspensionByTrustee(trustee, trusteeWallet, looper, nodeSet):
    node = nodeSet[-1]
    nodeNym = hexToFriendly(node.nodestack.local.signer.verhex)
    suspendNode(looper, trustee, trusteeWallet, nodeNym, node.name)
    for n in nodeSet[:-1]:
        looper.run(eventually(checkNodeNotInNodeReg, n, node.name))
    looper.run(eventually(checkNodeNotInNodeReg, trustee, node.name))


def testTrusteeCannotChangeVerkey(trustee, trusteeWallet, looper, nodeSet,
                                  anotherTrustee, anotherTGB, anotherSteward,
                                  anotherSponsor):
    for identity in (anotherTrustee, anotherTGB, anotherSteward, anotherSponsor):
        # Trustee cannot change verkey
        with pytest.raises(AssertionError):
            _, wallet = identity
            changeVerkey(looper, trustee, trusteeWallet, wallet.defaultId, '')
        # Identity owner can change verkey
        changeVerkey(looper, *identity, wallet.defaultId, '')
