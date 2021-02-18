# Some unit tests for upgrader
import pytest

import indy_common
from indy_common.constants import APP_NAME
from indy_common.version import src_version_cls
from indy_node.server.upgrader import Upgrader
from indy_node.utils.node_control_utils import NodeControlUtil, DebianVersion


some_pkg_name = 'some_package'


class PkgDebianVersion(DebianVersion):
    def __init__(self, pkg_name, version, *args, **kwargs):
        super().__init__(
            version,
            upstream_cls=indy_common.version.src_version_cls(pkg_name),
            *args, **kwargs
        )


@pytest.fixture(autouse=True)
def node_control_util_patched(monkeypatch, request):
    def pkg_version(pkg_name, version):
        return (
            PkgDebianVersion(
                pkg_name or some_pkg_name, version) if version else None
        )

    def pkg_info(pkg_name, version, deps):
        def wrapped(*x):
            return (pkg_version(pkg_name, version), deps)
        return wrapped

    def latest_pkg_ver(pkg_name, version):
        def wrapped(*x, **y):
            return pkg_version(pkg_name, version)
        return wrapped

    marker = request.node.get_closest_marker('pkg_info')
    if marker:
        assert len(marker.args) > 1
        monkeypatch.setattr(
            NodeControlUtil, 'curr_pkg_info',
            pkg_info(
                marker.kwargs.get('pkg_name'),
                marker.args[0],
                marker.args[1]
            )
        )

    marker = request.node.get_closest_marker('latest_pkg_ver')
    if marker:
        assert len(marker.args) > 0
        monkeypatch.setattr(
            NodeControlUtil, 'get_latest_pkg_version',
            latest_pkg_ver(
                marker.kwargs.get('pkg_name'),
                marker.args[0]
            )
        )


@pytest.mark.parametrize(
    'lower_version,higher_version',
    [
        ('0.0.5', '0.0.6'),
        ('0.1.2', '0.2.6'),
        ('1.10.2', '2.0.6'),
        ('1.2.3.dev1', '1.2.3rc1'),
        ('1.2.3.dev1', '1.2.3'),
        ('1.2.3.rc2', '1.2.3'),
    ]
)
def test_versions_comparison(lower_version, higher_version):
    assert Upgrader.compareVersions(higher_version, lower_version) == 1
    assert Upgrader.compareVersions(lower_version, higher_version) == -1
    assert Upgrader.compareVersions(higher_version, higher_version) == 0

    version_cls = src_version_cls(APP_NAME)
    lower_version = version_cls(lower_version)
    higher_version = version_cls(higher_version)
    assert not Upgrader.is_version_upgradable(higher_version, higher_version)
    assert Upgrader.is_version_upgradable(
        higher_version, higher_version, reinstall=True)
    assert Upgrader.is_version_upgradable(lower_version, higher_version)
    assert not Upgrader.is_version_upgradable(higher_version, lower_version)


def test_get_src_version_for_app(monkeypatch):
    called = 0

    def _f(*args, **kwargs):
        nonlocal called
        called += 1
        return (None, [])

    monkeypatch.setattr(NodeControlUtil, 'curr_pkg_info', _f)
    assert Upgrader.get_src_version(APP_NAME)
    assert not called
    Upgrader.get_src_version(APP_NAME, nocache=True)
    assert called


@pytest.mark.pkg_info('1:1.2.2-3', [])
def test_get_src_version_for(monkeypatch):
    assert (Upgrader.get_src_version(some_pkg_name) ==
            src_version_cls(some_pkg_name)('1.2.2'))


def test_check_upgrade_possible_invalid_target_version():
    assert 'invalid target version' in Upgrader.check_upgrade_possible(
        APP_NAME, '1.2.3.4')


@pytest.mark.pkg_info(None, [])
def test_check_upgrade_possible_pkg_not_installed():
    assert ('is not installed' in Upgrader.check_upgrade_possible(
        some_pkg_name, '1.2.3'))


@pytest.mark.pkg_info('1.2.2', ['pkg1'])
def test_check_upgrade_possible_invalid_top_level_pkg():
    assert ("doesn't belong to pool" in Upgrader.check_upgrade_possible(
        some_pkg_name, '1.2.3'))


@pytest.mark.pkg_info('1.2.2', [APP_NAME])
def test_check_upgrade_possible_not_gt_version():
    assert ("is not upgradable" in Upgrader.check_upgrade_possible(
        some_pkg_name, '1.2.2'))


@pytest.mark.pkg_info('1.2.2', [APP_NAME])
def test_check_upgrade_possible_not_ge_version_reinstall():
    assert ("is not upgradable" in Upgrader.check_upgrade_possible(
        some_pkg_name, '1.2.1', reinstall=True))


@pytest.mark.skip(reason='INDY-2026')
@pytest.mark.pkg_info('1.2.2', [APP_NAME])
#@pytest.mark.latest_pkg_ver(None) TODO INDY-2026
def test_check_upgrade_possible_no_pkg_with_target_version():
    target_ver = '1.2.3'
    assert (
        "for target version {} is not found".format(target_ver) in
        Upgrader.check_upgrade_possible(some_pkg_name, target_ver)
    )


@pytest.mark.pkg_info('1.2.2', [APP_NAME])
#@pytest.mark.latest_pkg_ver('1.2.3') TODO INDY-2026
def test_check_upgrade_possible_succeeded():
    target_ver = '1.2.3'
    assert not Upgrader.check_upgrade_possible(some_pkg_name, target_ver)
    assert not Upgrader.check_upgrade_possible(
        some_pkg_name, target_ver, reinstall=True)


@pytest.mark.pkg_info('1.2.2', [], pkg_name=APP_NAME)
#@pytest.mark.latest_pkg_ver('1.2.3') TODO INDY-2026
def test_check_upgrade_possible_succeeded_for_app_pkg():
    target_ver = '1.2.3'
    assert not Upgrader.check_upgrade_possible(APP_NAME, target_ver)
    assert not Upgrader.check_upgrade_possible(
        APP_NAME, target_ver, reinstall=True)


@pytest.mark.pkg_info('1.2.2', [APP_NAME])
#@pytest.mark.latest_pkg_ver('1.2.2') TODO INDY-2026
def test_check_upgrade_possible_reinstall_succeeded():
    assert not Upgrader.check_upgrade_possible(
        some_pkg_name, '1.2.2', reinstall=True)


@pytest.mark.pkg_info('1.2.2', [], pkg_name=APP_NAME)
#@pytest.mark.latest_pkg_ver('1.2.2') TODO INDY-2026
def test_check_upgrade_possible_reinstall_succeeded_for_app_pkg():
    assert not Upgrader.check_upgrade_possible(
        APP_NAME, '1.2.2', reinstall=True)
