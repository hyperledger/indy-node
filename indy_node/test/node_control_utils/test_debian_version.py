import pytest

from plenum.common.version import InvalidVersionError

from indy_common.version import NodeVersion
from indy_node.utils.node_control_utils import DebianVersion, NodeControlUtil, ShellError

# TODO
# - conditionally skip all tests for non-debian systems
# - tests for all coparison operators
# - test for command line generated for comparison


class UpstreamTest(NodeVersion):
    pass


class DebianVersionTest(DebianVersion):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, upstream_cls=UpstreamTest, **kwargs)


@pytest.fixture(autouse=True)
def clear_cache():
    DebianVersionTest.clear_cache()


# TODO coverage
@pytest.mark.parametrize(
    'version',
    [
        '',
        '1:'
        '-1'
    ]
)
def test_invalid_no_upstream(version):
    with pytest.raises(InvalidVersionError):
        DebianVersionTest(version)


@pytest.mark.parametrize(
    'version',
    [
        'a:1.2.3',
        '12:3.4',
        '1.:2.3',
    ]
)
def test_invalid_epoch(version):
    with pytest.raises(InvalidVersionError):
        DebianVersionTest(version)


@pytest.mark.parametrize(
    'version',
    [
        'a1.2.3',
        '1.2.3:3',
        '1.2',
    ]
)
def test_invalid_upstream(version):
    with pytest.raises(InvalidVersionError):
        DebianVersionTest(version)


def test_invalid_upstream_keep_tilde():
    with pytest.raises(InvalidVersionError):
        DebianVersionTest('1.2.3~rc1', keep_tilde=True)


# TODO coverage
@pytest.mark.parametrize(
    'epoch,upstream,revision',
    [
        ('1', '1.2.3', ''),
        ('', '1.2.3~rc4', ''),
        ('', '1.2.3~rc4', '5'),
        ('', '1.2.3~dev4', '5'),
    ]
)
def test_valid_version(epoch, upstream, revision):
    version = "{}{}{}".format(
        epoch + ':' if epoch else '',
        upstream,
        '-' + revision if revision else ''
    )

    dv = DebianVersionTest(version)
    epoch = epoch if epoch else None
    upstream = UpstreamTest(upstream.replace('~', '.'))
    revision = revision if revision else None

    assert dv.epoch == epoch
    assert dv.upstream == upstream
    assert dv.revision == revision
    assert dv.full == version
    assert dv.parts == (epoch, upstream, revision)
    assert dv.release == version
    assert dv.release_parts == (epoch, upstream, revision)


def test_compare_equal(monkeypatch):
    called = 0
    run_shell_script = NodeControlUtil.run_shell_script

    def _f(*args, **kwargs):
        nonlocal called
        called += 1
        return run_shell_script(*args, **kwargs)

    monkeypatch.setattr(NodeControlUtil, 'run_shell_script', _f)
    assert DebianVersionTest('1.2.3') == DebianVersionTest('1.2.3')
    assert not called


def test_compare_called_once(monkeypatch):
    called = 0
    run_shell_script = NodeControlUtil.run_shell_script

    def _f(*args, **kwargs):
        nonlocal called
        called += 1
        return run_shell_script(*args, **kwargs)

    monkeypatch.setattr(NodeControlUtil, 'run_shell_script', _f)
    assert DebianVersionTest('1.2.3') > DebianVersionTest('1.2.2')
    assert DebianVersionTest('1.2.3') > DebianVersionTest('1.2.2')
    assert DebianVersionTest('1.2.2') < DebianVersionTest('1.2.3')
    assert called == 1


@pytest.mark.parametrize(
    'v1,v2,expected',
    [
        ('1.2.3', '1.2.2', True),
        ('1.2.3~dev1', '1.2.3', False),
        ('1.2.3~dev2', '1.2.3~dev1', True),
        ('1.2.3~rc1', '1.2.3', False),
        ('1.2.3~rc1', '1.2.3~dev1', True),
        ('1.2.3~rc2', '1.2.3~rc1', True),
    ]
)
def test_compare_valid(v1, v2, expected):
    res = DebianVersionTest(v1) > DebianVersionTest(v2)
    assert res if expected else not res


def test_compare_shell_error(monkeypatch):
    run_shell_script = NodeControlUtil.run_shell_script

    def _f(command, *args, **kwargs):
        return run_shell_script('unknown command run', *args, **kwargs)

    monkeypatch.setattr(NodeControlUtil, 'run_shell_script', _f)
    with pytest.raises(ShellError):
        DebianVersionTest('1.2.3') > DebianVersionTest('1.2.2')
