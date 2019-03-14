import pytest

from indy_common.node_version_fallback import (
    InvalidVersionError, NodeVersionFallback,
)


def test_node_version_fallback_str():
    version = '1.2.3'
    assert str(NodeVersionFallback(version)) == version


def test_node_version_fallback_repr():
    version = '1.2.3'
    assert (repr(NodeVersionFallback(version)) ==
            "{}(version='{}')".format(NodeVersionFallback.__name__, version))


@pytest.mark.parametrize(
    'version',
    [
        1, [], {},
        '1',
        '1.2',
        '1.2.3.4',
        '1:1.2.3',
        '1.2.3+4',
        '1.2.3post4',
        '1.2.3dev',
        '1.2.3rc',
        '1.2.3a',
        '1.2.3b',
        # valid PEP440:
        #  alpha prerelease
        #  beta prerelease
        #  postrelease
        #  epoch
        #  local version
        #  parts num != 3
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
def test_node_version_fallback_init_invalid(version):
    with pytest.raises(InvalidVersionError):
        NodeVersionFallback(version)


@pytest.mark.parametrize(
    'version',
    [
        '1.2.3',
        '1.2.3.dev1',
        '1.2.3dev1',
        '1.2.3.dev.1',
        '1.2.3.rc1',
        '1.2.3rc1',
        '1.2.3.rc.1',
    ]
)
def test_node_version_fallback_init_valid(version):
    NodeVersionFallback(version)


def test_sem_ver_base_api():
    assert NodeVersionFallback('1.2.3').major == 1
    assert NodeVersionFallback('1.2.3').minor == 2
    assert NodeVersionFallback('1.2.3').patch == 3


def test_node_version_fallback_comparison_operators():
    with pytest.raises(TypeError):
        assert NodeVersionFallback('1.2.2') < NodeVersionFallback('1.2.3')
    with pytest.raises(TypeError):
        assert NodeVersionFallback('1.2.3') > NodeVersionFallback('1.2.2')
    with pytest.raises(TypeError):
        assert NodeVersionFallback('1.2.2') <= NodeVersionFallback('1.2.3')
    with pytest.raises(TypeError):
        assert NodeVersionFallback('1.2.3') <= NodeVersionFallback('1.2.3')
    with pytest.raises(TypeError):
        assert NodeVersionFallback('1.2.3') >= NodeVersionFallback('1.2.2')
    with pytest.raises(TypeError):
        assert NodeVersionFallback('1.2.2') >= NodeVersionFallback('1.2.2')

    assert NodeVersionFallback('1.2.2') == NodeVersionFallback('1.2.2')
    assert NodeVersionFallback('1.2.2') != NodeVersionFallback('1.2.3')


def test_node_version_fallback_upstream():
    pv = NodeVersionFallback('1.2.3')
    assert pv.upstream is pv


def test_node_version_fallback_public():
    assert NodeVersionFallback('1.2.3.dev2').parts == (1, 2, 3, 'dev', 2)
    assert NodeVersionFallback('1.2.3.rc3').parts == (1, 2, 3, 'rc', 3)
    assert NodeVersionFallback('1.2.3').parts == (1, 2, 3, None, None)


def test_node_version_fallback_parts():
    assert NodeVersionFallback('1.2.3.dev2').parts == (1, 2, 3, 'dev', 2)
    assert NodeVersionFallback('1.2.3.rc3').parts == (1, 2, 3, 'rc', 3)
    assert NodeVersionFallback('1.2.3').parts == (1, 2, 3, None, None)


@pytest.mark.parametrize(
    'version',
    [
        '1.2.3',
        '1.2.3.dev2',
        '1.2.3rc1',
    ]
)
def test_node_version_fallback_base_api(version):
    v = NodeVersionFallback(version)
    assert v.full == version
    assert v.public == version
    assert v.release_parts == v.parts[:3]
    assert v.release == '.'.join(map(str, v.release_parts))
