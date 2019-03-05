import pytest

from plenum.common.version import InvalidVersionError

from indy_common.version import (
    SchemaVersion, TopPackageDefaultVersion, NodeVersion
)


def test_schema_version():
    for version in ['', '1', '1.2.3.4', '1.2.a']:
        with pytest.raises(InvalidVersionError):
            SchemaVersion(version)
    SchemaVersion('1.2')
    SchemaVersion('1.2.3')


def test_top_package_default_version():
    for version in ['', '1', '1.2.3.4', '1.2.a']:
        with pytest.raises(InvalidVersionError):
            TopPackageDefaultVersion(version)
    TopPackageDefaultVersion('1.2')
    TopPackageDefaultVersion('1.2.3')


# valid PEP440:
#  alpha prerelease
#  beta prerelease
#  postrelease
#  epoch
#  local verion
#  parts num != 3
@pytest.mark.parametrize(
    'version',
    [
        '1.2.3a1',
        '1.2.3b2',
        '1.2.3.post1',
        '1!1.2.3',
        '1.2.3+1',
        '1',
        '1.2',
        '1.2.3.4'
    ]
)
def test_node_version_invalid_value(version):
    with pytest.raises(InvalidVersionError):
        NodeVersion(version)


@pytest.mark.parametrize(
    'version',
    [
        '1.2.3',
        '1.2.3.rc1',
        '1.2.3.dev2',
    ]
)
def test_node_version_valid(version):
    NodeVersion(version)
