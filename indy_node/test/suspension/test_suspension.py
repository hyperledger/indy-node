import pytest

from plenum.common.exceptions import RequestRejectedException
from indy_node.test.suspension.helper import sdk_suspend_role
from plenum.common.util import randomString
from plenum.test.pool_transactions.helper import demote_node, sdk_add_new_nym
from stp_core.loop.eventually import eventually
from stp_core.common.log import getlogger
from plenum.common.constants import STEWARD_STRING, TRUSTEE_STRING
from plenum.test.pool_transactions.test_suspend_node import \
    checkNodeNotInNodeReg
from indy_common.constants import ENDORSER_STRING

logger = getlogger()


@pytest.fixture(scope="module")
def another_trustee(looper, nodeSet, sdk_pool_handle, sdk_wallet_trustee):
    return sdk_add_new_nym(looper, sdk_pool_handle,
                           sdk_wallet_trustee, 'newTrustee', TRUSTEE_STRING)


@pytest.fixture(scope="module")
def another_steward(looper, nodeSet, sdk_pool_handle, sdk_wallet_trustee):
    return sdk_add_new_nym(looper, sdk_pool_handle,
                           sdk_wallet_trustee, 'newSteward', STEWARD_STRING)


@pytest.fixture(scope="module")
def another_steward1(looper, nodeSet, sdk_pool_handle, sdk_wallet_trustee):
    return sdk_add_new_nym(looper, sdk_pool_handle,
                           sdk_wallet_trustee, 'newSteward1', STEWARD_STRING)


@pytest.fixture(scope="module")
def another_endorser(looper, nodeSet, sdk_pool_handle, sdk_wallet_trustee):
    return sdk_add_new_nym(looper, sdk_pool_handle,
                           sdk_wallet_trustee, 'newEndorser', ENDORSER_STRING)


@pytest.fixture(scope="module")
def another_endorser1(looper, nodeSet, sdk_pool_handle, sdk_wallet_trustee):
    return sdk_add_new_nym(looper, sdk_pool_handle,
                           sdk_wallet_trustee, 'newEndorser1', ENDORSER_STRING)


def testTrusteeAddingAnotherTrustee(another_trustee):
    pass


def testTrusteeAddingSteward(looper, sdk_pool_handle, another_steward):
    # The new Steward adds a ENDORSER
    sdk_add_new_nym(looper, sdk_pool_handle, another_steward, role=ENDORSER_STRING)


def testTrusteeAddingEndorser(looper, sdk_pool_handle, another_endorser):
    # The new TEndorser adds a NYM
    sdk_add_new_nym(looper, sdk_pool_handle, another_endorser)


def testStewardSuspensionByTrustee(looper, sdk_pool_handle,
                                   another_trustee, another_steward):
    _, did_stew = another_steward
    sdk_suspend_role(looper, sdk_pool_handle, another_trustee, did_stew)
    with pytest.raises(RequestRejectedException):
        sdk_add_new_nym(looper, sdk_pool_handle,
                        another_steward, role=ENDORSER_STRING)


def testEndorserSuspensionByTrustee(
        looper, sdk_pool_handle, another_trustee, another_endorser):
    _, did_ta = another_endorser
    sdk_suspend_role(looper, sdk_pool_handle, another_trustee, did_ta)
    with pytest.raises(RequestRejectedException):
        sdk_add_new_nym(looper, sdk_pool_handle,
                        another_endorser, alias=randomString())


def testTrusteeSuspensionByTrustee(looper, sdk_pool_handle, sdk_wallet_trustee,
                                   another_trustee, another_steward1):
    # trustee suspension by trustee is succeed
    _, did = another_trustee
    sdk_suspend_role(looper, sdk_pool_handle, sdk_wallet_trustee, did)

    # trustee suspension by steward1 is failed
    _, did = sdk_wallet_trustee
    with pytest.raises(RequestRejectedException) as e:
        sdk_suspend_role(looper, sdk_pool_handle, another_steward1, did)
    e.match("Not enough TRUSTEE signatures")


# Keep the test below at the end of the suite since it will make one of the
# nodes inactive, unless you are planning to add new nodes.
def testValidatorSuspensionByTrustee(sdk_wallet_trustee, sdk_pool_handle, looper, nodeSet):
    node = nodeSet[-1]
    demote_node(looper, sdk_wallet_trustee, sdk_pool_handle, node)
    for n in nodeSet[:-1]:
        looper.run(eventually(checkNodeNotInNodeReg, n, node.name))
