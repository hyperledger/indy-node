# Some unit tests for upgrader
from sovrin_node.server.upgrader import Upgrader


def testVersions():
    assert Upgrader.compareVersions('0.0.5', '0.0.6') == 1
    assert Upgrader.compareVersions('0.0.6', '0.0.5') == -1
    assert Upgrader.compareVersions('0.0.6', '0.0.6') == 0
    assert not Upgrader.is_version_upgradable('0.0.6', '0.0.6')
    assert Upgrader.is_version_upgradable('0.0.6', '0.0.6', reinstall=True)
    assert Upgrader.is_version_upgradable('0.0.5', '0.0.6')
    assert Upgrader.is_version_upgradable('0.0.6', '0.0.5')
