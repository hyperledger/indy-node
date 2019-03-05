# Some unit tests for upgrader
import pytest

from plenum.common.version import SemVerReleaseVersion

from indy_node.server.upgrader import Upgrader


def comparator_test(lower_version, higher_version):
    assert Upgrader.compareVersions(higher_version, lower_version) == 1
    assert Upgrader.compareVersions(lower_version, higher_version) == -1
    assert Upgrader.compareVersions(higher_version, higher_version) == 0

    lower_version = SemVerReleaseVersion(lower_version)
    higher_version = SemVerReleaseVersion(higher_version)
    assert not Upgrader.is_version_upgradable(higher_version, higher_version)
    assert Upgrader.is_version_upgradable(
        higher_version, higher_version, reinstall=True)
    assert Upgrader.is_version_upgradable(lower_version, higher_version)
    assert not Upgrader.is_version_upgradable(higher_version, lower_version)


@pytest.mark.parametrize(
    'lower_version,higher_version',
    [
        ('0.0.5', '0.0.6'),
        ('0.1.2', '0.2.6'),
        ('1.10.2', '2.0.6'),
    ]
)
def test_versions(lower_version, higher_version):
    comparator_test(lower_version, higher_version)
