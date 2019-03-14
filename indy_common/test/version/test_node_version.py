# TODO it's a copy-paste of common.version:
# remove once plenum is merged to node
import pytest

from indy_common.node_version import NodeVersion, InvalidVersionError


# valid PEP440:
#  alpha prerelease
#  beta prerelease
#  postrelease
#  epoch
#  local version
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
        # '1.2', TODO uncomment once new release logic becomes completed
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


def test_node_version_parts():
    assert NodeVersion('1.2.3.dev2').parts == (1, 2, 3, 'dev', 2)
    assert NodeVersion('1.2.3.rc3').parts == (1, 2, 3, 'rc', 3)
    assert NodeVersion('1.2.3').parts == (1, 2, 3, None, None)


def test_node_version_upstream():
    pv = NodeVersion('1.2.3')
    assert pv.upstream is pv
