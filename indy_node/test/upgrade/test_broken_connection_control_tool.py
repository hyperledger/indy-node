import dateutil
import dateutil.tz
import pytest

from datetime import datetime, timedelta
from copy import deepcopy
from indy_common.constants import START
from indy_node.test.upgrade.conftest import patch_packet_mgr_output, EXT_PKT_NAME, EXT_PKT_VERSION

from indy_node.server.upgrader import Upgrader
from indy_node.test.upgrade.helper import sdk_ensure_upgrade_sent, bumpedVersion
from plenum.test.helper import randomText

from stp_core.common.log import getlogger

delta = 2
logger = getlogger()


@pytest.fixture(scope='function')
def pckg():
    return (EXT_PKT_NAME, EXT_PKT_VERSION)


@pytest.fixture(scope="module")
def tconf(tconf):
    old_delta = tconf.MinSepBetweenNodeUpgrades
    tconf.MinSepBetweenNodeUpgrades = delta
    yield tconf
    tconf.MinSepBetweenNodeUpgrades = old_delta


@pytest.fixture(scope='function')
def skip_functions():
    # Do this to prevent exceptions because of node_control_tool absence
    old_action_failed = deepcopy(Upgrader._action_failed)

    Upgrader._action_failed = lambda *args, **kwargs: 1
    yield
    Upgrader._action_failed = old_action_failed


def test_node_doesnt_retry_upgrade(looper, nodeSet, validUpgrade, nodeIds,
                                   sdk_pool_handle, sdk_wallet_trustee, tconf,
                                   skip_functions):
    schedule = {}
    unow = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    startAt = unow + timedelta(seconds=delta)
    for i in nodeIds:
        schedule[i] = datetime.isoformat(startAt)
        startAt = startAt + timedelta(seconds=delta)
    validUpgrade['schedule'] = schedule

    # Emulating connection problems
    for node in nodeSet:
        node.upgrader.retry_limit = 0

    # Send upgrade
    sdk_ensure_upgrade_sent(looper, sdk_pool_handle,
                            sdk_wallet_trustee, validUpgrade)
    looper.runFor(len(nodeIds) * delta)

    # Every node, including bad_node, tried to upgrade only once
    for node in nodeSet:
        assert node.upgrader.spylog.count(Upgrader.processLedger.__name__) == 1
