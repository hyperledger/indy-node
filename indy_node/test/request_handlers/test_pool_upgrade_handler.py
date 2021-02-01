import pytest
from indy_common.constants import POOL_UPGRADE, ACTION, START, PACKAGE, APP_NAME, REINSTALL
from indy_node.server.request_handlers.config_req_handlers.pool_upgrade_handler import PoolUpgradeHandler
from plenum.common.constants import VERSION, TXN_PAYLOAD, TXN_PAYLOAD_DATA
from plenum.common.exceptions import InvalidClientRequest

from plenum.common.request import Request
from plenum.common.util import randomString
from plenum.test.testing_utils import FakeSomething

from indy_common.version import src_version_cls
from indy_node.server.upgrader import Upgrader
from indy_node.utils.node_control_utils import NodeControlUtil, DebianVersion


@pytest.fixture(scope='function')
def pool_upgrade_request():
    return Request(identifier=randomString(),
                   reqId=5,
                   operation={
                       'type': POOL_UPGRADE,
                       ACTION: START,
                       PACKAGE: 'smth',
                       VERSION: '1.2.3'
                   })


@pytest.fixture(scope='function')
def pool_upgrade_handler(write_auth_req_validator):
    return PoolUpgradeHandler(
        None,
        FakeSomething(check_upgrade_possible=Upgrader.check_upgrade_possible),
        write_auth_req_validator,
        FakeSomething()
    )


@pytest.fixture(scope='function')
def pkg_version(pool_upgrade_request):
    return DebianVersion(
        '1.1.1',
        upstream_cls=src_version_cls(
            pool_upgrade_request.operation[PACKAGE])
    )


@pytest.mark.request_handlers
def test_pool_upgrade_static_validation_fails_action(pool_upgrade_handler,
                                                     pool_upgrade_request):
    pool_upgrade_request.operation[ACTION] = 'smth'
    with pytest.raises(InvalidClientRequest) as e:
        pool_upgrade_handler.static_validation(pool_upgrade_request)
    e.match('not a valid action')


@pytest.mark.request_handlers
def test_pool_upgrade_static_validation_fails_schedule(pool_upgrade_handler,
                                                       pool_upgrade_request):
    pool_upgrade_handler.pool_manager.getNodesServices = lambda: 1
    pool_upgrade_handler.upgrader.isScheduleValid = lambda schedule, node_srvs, force: (False, '')
    with pytest.raises(InvalidClientRequest) as e:
        pool_upgrade_handler.static_validation(pool_upgrade_request)
    e.match('not a valid schedule since')


@pytest.mark.request_handlers
def test_pool_upgrade_static_validation_passes(pool_upgrade_handler,
                                               pool_upgrade_request):
    pool_upgrade_handler.pool_manager.getNodesServices = lambda: 1
    pool_upgrade_handler.upgrader.isScheduleValid = lambda schedule, node_srvs, force: (True, '')
    pool_upgrade_handler.static_validation(pool_upgrade_request)


@pytest.mark.request_handlers
def test_pool_upgrade_dynamic_validation_fails_pckg(pool_upgrade_handler,
                                                    pool_upgrade_request,
                                                    tconf):
    pool_upgrade_request.operation[PACKAGE] = ''
    with pytest.raises(InvalidClientRequest) as e:
        pool_upgrade_handler.dynamic_validation(pool_upgrade_request, 0)
    e.match('Upgrade package name is empty')


@pytest.mark.request_handlers
def test_pool_upgrade_dynamic_validation_fails_not_installed(
        monkeypatch,
        pool_upgrade_handler,
        pool_upgrade_request,
        tconf):
    monkeypatch.setattr(NodeControlUtil, 'curr_pkg_info',
                        lambda *x: (None, None))
    with pytest.raises(InvalidClientRequest) as e:
        pool_upgrade_handler.dynamic_validation(pool_upgrade_request, 0)
    e.match('is not installed and cannot be upgraded')


@pytest.mark.request_handlers
def test_pool_upgrade_dynamic_validation_fails_belong(
        monkeypatch,
        pool_upgrade_handler,
        pool_upgrade_request,
        tconf):
    monkeypatch.setattr(NodeControlUtil, 'curr_pkg_info',
                        lambda *x: ('1.1.1', ['some_pkg']))
    with pytest.raises(InvalidClientRequest) as e:
        pool_upgrade_handler.dynamic_validation(pool_upgrade_request, 0)
    e.match('doesn\'t belong to pool')


@pytest.mark.request_handlers
def test_pool_upgrade_dynamic_validation_fails_upgradable(
        monkeypatch,
        pool_upgrade_handler,
        pool_upgrade_request,
        pkg_version,
        tconf):
    monkeypatch.setattr(
        NodeControlUtil, 'curr_pkg_info',
        lambda *x: (pkg_version, [APP_NAME])
    )
    pool_upgrade_request.operation[VERSION] = pkg_version.upstream.full
    pool_upgrade_request.operation[REINSTALL] = False
    with pytest.raises(InvalidClientRequest) as e:
        pool_upgrade_handler.dynamic_validation(pool_upgrade_request, 0)
    e.match('Version {} is not upgradable'.format(pkg_version.upstream.full))


@pytest.mark.request_handlers
def test_pool_upgrade_dynamic_validation_fails_scheduled(
        monkeypatch,
        pool_upgrade_handler,
        pool_upgrade_request,
        pkg_version,
        tconf):
    monkeypatch.setattr(
        NodeControlUtil, 'curr_pkg_info',
        lambda *x: (pkg_version, [APP_NAME])
    )
    monkeypatch.setattr(
        NodeControlUtil, 'get_latest_pkg_version',
        lambda *x, **y: pkg_version
    )
    pool_upgrade_request.operation[VERSION] = pkg_version.upstream.full
    pool_upgrade_request.operation[REINSTALL] = True
    pool_upgrade_handler.upgrader.get_upgrade_txn = \
        lambda predicate, reverse: \
            {TXN_PAYLOAD: {TXN_PAYLOAD_DATA: {ACTION: START}}}

    with pytest.raises(InvalidClientRequest) as e:
        pool_upgrade_handler.dynamic_validation(pool_upgrade_request, 0)
    e.match('is already scheduled')


@pytest.mark.request_handlers
def test_pool_upgrade_dynamic_validation_passes(
        monkeypatch,
        pool_upgrade_handler,
        pool_upgrade_request,
        pkg_version,
        tconf):
    monkeypatch.setattr(
        NodeControlUtil, 'curr_pkg_info',
        lambda *x: (pkg_version, [APP_NAME])
    )
    monkeypatch.setattr(
        NodeControlUtil, 'get_latest_pkg_version',
        lambda *x, **y: pkg_version
    )
    pool_upgrade_request.operation[VERSION] = pkg_version.upstream.full
    pool_upgrade_request.operation[REINSTALL] = True
    pool_upgrade_handler.upgrader.get_upgrade_txn = \
        lambda predicate, reverse: \
            {TXN_PAYLOAD: {TXN_PAYLOAD_DATA: {}}}
    pool_upgrade_handler.write_req_validator.validate = lambda a, b: 0
    pool_upgrade_handler.dynamic_validation(pool_upgrade_request, 0)
