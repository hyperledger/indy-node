import pytest

from plenum.common.version import InvalidVersion

from indy_common.version import NodeVersion


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
    with pytest.raises(InvalidVersion):
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
