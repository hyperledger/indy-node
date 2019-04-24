from datetime import datetime, timedelta

import dateutil.tz
import pytest

from stp_core.loop.eventually import eventually
from plenum.common.constants import VERSION
from plenum.test.helper import randomText

from indy_common.constants import START, FORCE, APP_NAME
from indy_common.version import src_version_cls
from indy_node.utils.node_control_utils import NodeControlUtil, DebianVersion
from indy_node.server.upgrader import Upgrader

from indy_node.test import waits
from indy_node.test.upgrade.helper import bumpedVersion, \
    checkUpgradeScheduled, bumpVersion, sdk_ensure_upgrade_sent


@pytest.fixture(scope='module')
def nodeIds(nodeSet):
    return nodeSet[0].poolManager.nodeIds


EXT_PKT_NAME = 'SomeTopLevelPkt'
EXT_PKT_VERSION = '7.88.999'


# TODO review and improve: which contexts are goinig to be satisfied
# by the following mocks
def patch_packet_mgr_output(monkeypatch, pkg_name, pkg_version, new_version):
    if pkg_name != APP_NAME:
        node_package = (APP_NAME, '0.0.1')
        EXT_TOP_PKT_DEPS = [("aa", "1.1.1"), ("bb", "2.2.2")]
        PACKAGE_MNG_EXT_PTK_OUTPUT = (
            "Package: {}\nVersion: {}\n"
            "Depends: {}, {} (= {}), {} (= {})\n"
            .format(pkg_name, pkg_version, APP_NAME,
                    *EXT_TOP_PKT_DEPS[0], *EXT_TOP_PKT_DEPS[1])
        )
        top_level_package = (pkg_name, pkg_version)
        plenum_package = ('indy-plenum', '0.0.3')
        top_level_package_with_version = '{}={}'.format(*top_level_package)
        top_level_package_dep1_with_version = '{}={}'.format(*EXT_TOP_PKT_DEPS[0])
        top_level_package_dep2_with_version = '{}={}'.format(*EXT_TOP_PKT_DEPS[1])
        node_package_with_version = '{}={}'.format(*node_package)
        plenum_package_with_version = '{}={}'.format(*plenum_package)
        mock_info = {
            top_level_package_with_version: "{}{} (= {}) {} (= {}), {} (= {})".format(
                randomText(100), *node_package, *EXT_TOP_PKT_DEPS[0], *EXT_TOP_PKT_DEPS[1]),
            node_package_with_version: '{}{} (= {}){}{}'.format(
                randomText(100), *plenum_package, randomText(100), randomText(100)),
            plenum_package_with_version: '{}'.format(randomText(100)),
            top_level_package_dep1_with_version: '{}{} (= {})'.format(randomText(100), *plenum_package),
            top_level_package_dep2_with_version: '{}{} (= {})'.format(randomText(100), *node_package)
        }

        def mock_get_info_from_package_manager(package):
            if package.startswith(pkg_name):
                return mock_info.get(top_level_package_with_version, "")
            return mock_info.get(package, "")

        #monkeypatch.setattr(NodeControlUtil, '_get_info_from_package_manager',
        #                    lambda x: mock_get_info_from_package_manager(x))
        monkeypatch.setattr(NodeControlUtil, '_get_curr_info', lambda *x: PACKAGE_MNG_EXT_PTK_OUTPUT)
    else:
        #monkeypatch.setattr(
        #    NodeControlUtil, '_get_info_from_package_manager',
        #    lambda package: "Package: {}\nVersion: {}\n".format(APP_NAME, pkg_version) if package == APP_NAME else ""
        #)
        monkeypatch.setattr(
            NodeControlUtil, '_get_curr_info',
            lambda *x: "Package: {}\nVersion: {}\n".format(APP_NAME, pkg_version)
        )

    monkeypatch.setattr(NodeControlUtil, 'update_package_cache', lambda *x: None)
    monkeypatch.setattr(
        NodeControlUtil, 'get_latest_pkg_version',
        lambda *x, **y: DebianVersion(
            new_version, upstream_cls=src_version_cls(pkg_name))
    )


@pytest.fixture(scope='function', params=[
    (EXT_PKT_NAME, EXT_PKT_VERSION),
    (APP_NAME, Upgrader.get_src_version(APP_NAME).release)
])
def pckg(request):
    return request.param


@pytest.fixture(scope='function')
def validUpgrade(nodeIds, tconf, monkeypatch, pckg):
    schedule = {}
    unow = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    startAt = unow + timedelta(seconds=100)
    acceptableDiff = tconf.MinSepBetweenNodeUpgrades + 1
    for i in nodeIds:
        schedule[i] = datetime.isoformat(startAt)
        startAt = startAt + timedelta(seconds=acceptableDiff + 3)

    new_version = bumpedVersion(pckg[1])
    patch_packet_mgr_output(monkeypatch, pckg[0], pckg[1], new_version)

    return dict(name='upgrade-{}'.format(randomText(3)), version=new_version,
                action=START, schedule=schedule, timeout=1, package=pckg[0],
                sha256='db34a72a90d026dae49c3b3f0436c8d3963476c77468ad955845a1ccf7b03f55')


@pytest.fixture(scope='function')
def validUpgradeExpForceFalse(validUpgrade):
    nup = validUpgrade.copy()
    nup.update({FORCE: False})
    nup.update({VERSION: bumpVersion(validUpgrade[VERSION])})
    return nup


@pytest.fixture(scope='function')
def validUpgradeExpForceTrue(validUpgradeExpForceFalse):
    nup = validUpgradeExpForceFalse.copy()
    nup.update({FORCE: True})
    nup.update({VERSION: bumpVersion(validUpgradeExpForceFalse[VERSION])})
    return nup


@pytest.fixture(scope='function')
def validUpgradeSent(looper, nodeSet, tdir, sdk_pool_handle, sdk_wallet_trustee,
                     validUpgrade):
    sdk_ensure_upgrade_sent(looper, sdk_pool_handle,
                            sdk_wallet_trustee, validUpgrade)


@pytest.fixture(scope='function')
def validUpgradeSentExpForceFalse(
        looper,
        nodeSet,
        tdir,
        sdk_pool_handle,
        sdk_wallet_trustee,
        validUpgradeExpForceFalse):
    sdk_ensure_upgrade_sent(looper, sdk_pool_handle,
                            sdk_wallet_trustee, validUpgradeExpForceFalse)


@pytest.fixture(scope='function')
def validUpgradeSentExpForceTrue(looper, nodeSet, tdir, sdk_pool_handle,
                                 sdk_wallet_trustee, validUpgradeExpForceTrue):
    sdk_ensure_upgrade_sent(looper, sdk_pool_handle,
                            sdk_wallet_trustee, validUpgradeExpForceTrue)


@pytest.fixture(scope='function')
def upgradeScheduled(validUpgradeSent, looper, nodeSet, validUpgrade):
    looper.run(
        eventually(
            checkUpgradeScheduled,
            nodeSet,
            validUpgrade[VERSION],
            retryWait=1,
            timeout=waits.expectedUpgradeScheduled()))


@pytest.fixture(scope='function')
def upgradeScheduledExpForceFalse(validUpgradeSentExpForceFalse, looper,
                                  nodeSet, validUpgradeExpForceFalse):
    looper.run(eventually(checkUpgradeScheduled, nodeSet,
                          validUpgradeExpForceFalse[VERSION], retryWait=1,
                          timeout=waits.expectedUpgradeScheduled()))


@pytest.fixture(scope='function')
def upgradeScheduledExpForceTrue(validUpgradeSentExpForceTrue, looper, nodeSet,
                                 validUpgradeExpForceTrue):
    looper.run(eventually(checkUpgradeScheduled, nodeSet,
                          validUpgradeExpForceTrue[VERSION], retryWait=1,
                          timeout=waits.expectedUpgradeScheduled()))


@pytest.fixture(scope='function')
def invalidUpgrade(nodeIds, tconf, validUpgrade):
    nup = validUpgrade.copy()
    schedule = {}
    unow = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    startAt = unow + timedelta(seconds=60)
    acceptableDiff = tconf.MinSepBetweenNodeUpgrades + 1
    for i in nodeIds:
        schedule[i] = datetime.isoformat(startAt)
        startAt = startAt + timedelta(seconds=acceptableDiff - 3)
    nup.update(dict(name='upgrade-14', version=bumpedVersion(), action=START,
                    schedule=schedule,
                    sha256='46c715a90b1067142d548cb1f1405b0486b32b1a27d418ef3a52bd976e9fae50',
                    timeout=10))
    return nup
