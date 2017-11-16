# Some unit tests for upgrader
from indy_node.server.upgrader import Upgrader


def comparator_test(lower_versrion, higher_version):
    assert Upgrader.compareVersions(lower_versrion, higher_version) == 1
    assert Upgrader.compareVersions(higher_version, lower_versrion) == -1
    assert Upgrader.compareVersions(higher_version, higher_version) == 0
    assert not Upgrader.is_version_upgradable(higher_version, higher_version)
    assert Upgrader.is_version_upgradable(
        higher_version, higher_version, reinstall=True)
    assert Upgrader.is_version_upgradable(lower_versrion, higher_version)
    assert not Upgrader.is_version_upgradable(higher_version, lower_versrion)


def test_versions():
    comparator_test('0.0.5', '0.0.6')
    comparator_test('0.1.2', '0.2.6')
    comparator_test('1.10.2', '2.0.6')
