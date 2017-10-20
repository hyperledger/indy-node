from copy import copy

import pytest

from indy_node.test import waits
from stp_core.loop.eventually import eventually
from plenum.common.constants import VERSION
from indy_common.constants import ACTION, CANCEL, JUSTIFICATION
from indy_node.test.upgrade.helper import checkUpgradeScheduled, \
    checkNoUpgradeScheduled
from indy_node.test.upgrade.conftest import validUpgrade, validUpgradeExpForceFalse, validUpgradeExpForceTrue


def send_upgrade_cmd(do, expect, upgrade_data):
    do('send POOL_UPGRADE name={name} version={version} sha256={sha256} '
       'action={action} schedule={schedule} timeout={timeout}',
       within=10,
       expect=expect, mapper=upgrade_data)


@pytest.fixture(scope="module")
def poolUpgradeSubmitted(be, do, trusteeCli, validUpgrade):
    be(trusteeCli)
    send_upgrade_cmd(do,
                     ['Sending pool upgrade',
                      'Pool Upgrade Transaction Scheduled'],
                     validUpgrade)


@pytest.fixture(scope="module")
def poolUpgradeScheduled(poolUpgradeSubmitted, poolNodesStarted, validUpgrade):
    nodes = poolNodesStarted.nodes.values()
    timeout = waits.expectedUpgradeScheduled()
    poolNodesStarted.looper.run(
        eventually(checkUpgradeScheduled, nodes,
                   validUpgrade[VERSION], retryWait=1, timeout=timeout))


@pytest.fixture(scope="module")
def poolUpgradeCancelled(poolUpgradeScheduled, be, do, trusteeCli,
                         validUpgrade):
    cancelUpgrade = copy(validUpgrade)
    cancelUpgrade[ACTION] = CANCEL
    cancelUpgrade[JUSTIFICATION] = '"not gonna give you one"'
    be(trusteeCli)
    do('send POOL_UPGRADE name={name} version={version} sha256={sha256} '
       'action={action} justification={justification}',
       within=10,
       expect=['Sending pool upgrade', 'Pool Upgrade Transaction Scheduled'],
       mapper=cancelUpgrade)


def test_pool_upgrade_rejected(be, do, newStewardCli, validUpgrade):
    """
    Pool upgrade done by a non trustee is rejected
    """
    be(newStewardCli)
    err_msg = "Pool upgrade failed: client request invalid: " \
              "UnauthorizedClientRequest('STEWARD cannot do POOL_UPGRADE'"
    send_upgrade_cmd(do,
                     ['Sending pool upgrade',
                      err_msg],
                     validUpgrade)


def testPoolUpgradeSent(poolUpgradeScheduled):
    pass


def testPoolUpgradeCancelled(poolUpgradeCancelled, poolNodesStarted):
    nodes = poolNodesStarted.nodes.values()
    timeout = waits.expectedNoUpgradeScheduled()
    poolNodesStarted.looper.run(
        eventually(checkNoUpgradeScheduled,
                   nodes, retryWait=1, timeout=timeout))


def send_force_false_upgrade_cmd(do, expect, upgrade_data):
    do('send POOL_UPGRADE name={name} version={version} sha256={sha256} '
       'action={action} schedule={schedule} timeout={timeout} force=False',
       within=10,
       expect=expect, mapper=upgrade_data)


def test_force_false_upgrade(
        be, do, trusteeCli, poolNodesStarted, validUpgradeExpForceFalse):
    be(trusteeCli)
    send_force_false_upgrade_cmd(do,
                                 ['Sending pool upgrade',
                                  'Pool Upgrade Transaction Scheduled'],
                                 validUpgradeExpForceFalse)
    poolNodesStarted.looper.run(
        eventually(
            checkUpgradeScheduled,
            poolNodesStarted.nodes.values(),
            validUpgradeExpForceFalse[VERSION],
            retryWait=1,
            timeout=10))


def send_force_true_upgrade_cmd(do, expect, upgrade_data):
    do('send POOL_UPGRADE name={name} version={version} sha256={sha256} '
       'action={action} schedule={schedule} timeout={timeout} force=True',
       within=10,
       expect=expect, mapper=upgrade_data)


def test_force_upgrade(be, do, trusteeCli, poolNodesStarted,
                       validUpgradeExpForceTrue):
    nodes = poolNodesStarted.nodes.values()
    for node in nodes:
        if node.name in ["Delta", "Gamma"]:
            node.stop()
            poolNodesStarted.looper.removeProdable(node)
    be(trusteeCli)
    send_force_true_upgrade_cmd(
        do, ['Sending pool upgrade'], validUpgradeExpForceTrue)

    def checksched():
        for node in nodes:
            if node.name not in ["Delta", "Gamma"]:
                assert node.upgrader.scheduledUpgrade
                assert node.upgrader.scheduledUpgrade[0] == validUpgradeExpForceTrue[VERSION]

    poolNodesStarted.looper.run(eventually(
        checksched, retryWait=1, timeout=10))


def send_reinstall_true_upgrade_cmd(do, expect, upgrade_data):
    do('send POOL_UPGRADE name={name} version={version} sha256={sha256} '
       'action={action} schedule={schedule} timeout={timeout} reinstall=True',
       within=10,
       expect=expect, mapper=upgrade_data)


def send_reinstall_false_upgrade_cmd(do, expect, upgrade_data):
    do('send POOL_UPGRADE name={name} version={version} sha256={sha256} '
       'action={action} schedule={schedule} timeout={timeout} reinstall=False',
       within=10,
       expect=expect, mapper=upgrade_data)
