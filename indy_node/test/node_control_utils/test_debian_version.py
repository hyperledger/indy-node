import pytest

from indy_node.utils.node_control_utils import DebianVersion, NodeControlUtil, ShellException

# TODO
# - conditionally skip all tests for non-debian systems
# - tests for all coparison operators


@pytest.fixture(autouse=True)
def clear_cache():
    DebianVersion.clear_cache()


def test_compare_equal(monkeypatch):
    called = 0
    run_shell_script = NodeControlUtil.run_shell_script

    def _f(*args, **kwargs):
        nonlocal called
        called += 1
        return run_shell_script(*args, **kwargs)

    monkeypatch.setattr(NodeControlUtil, 'run_shell_script', _f)
    assert DebianVersion('1.2.3') == DebianVersion('1.2.3')
    assert not called


def test_compare_called_once(monkeypatch):
    called = 0
    run_shell_script = NodeControlUtil.run_shell_script

    def _f(*args, **kwargs):
        nonlocal called
        called += 1
        return run_shell_script(*args, **kwargs)

    monkeypatch.setattr(NodeControlUtil, 'run_shell_script', _f)
    assert DebianVersion('1.2.3') > DebianVersion('1.2.2')
    assert DebianVersion('1.2.3') > DebianVersion('1.2.2')
    assert DebianVersion('1.2.2') < DebianVersion('1.2.3')
    assert called == 1


@pytest.mark.parametrize(
    'v1,v2,expected',
    [
        ('1.2.3', '1.2.2', True),
        ('1.2.3~1', '1.2.3', False),
        ('1.2.3~2', '1.2.3~1', True),
        ('1.2.3~rc.1', '1.2.3', False),
        ('1.2.3~rc.1', '1.2.3~1', True),
        ('1.2.3~rc.2', '1.2.3~rc.1', True),
    ]
)
def test_compare_valid(v1, v2, expected):
    res = DebianVersion(v1) > DebianVersion(v2)
    assert res if expected else not res


def test_compare_invalid():
    with pytest.raises(ShellException):
        DebianVersion('1.2.3') > DebianVersion('a1.2.3')


def test_compare_shell_error(monkeypatch):
    run_shell_script = NodeControlUtil.run_shell_script

    def _f(command, *args, **kwargs):
        return run_shell_script('unknown command run', *args, **kwargs)

    monkeypatch.setattr(NodeControlUtil, 'run_shell_script', _f)
    with pytest.raises(ShellException):
        DebianVersion('1.2.3') > DebianVersion('1.2.2')
