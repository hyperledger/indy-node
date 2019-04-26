import pytest
import shutil

from common.version import DigitDotVersion

from indy_common.constants import APP_NAME
from indy_common.version import src_version_cls
from indy_node.utils.node_control_utils import (
    NodeControlUtil, ShellError, DebianVersion
)

# TODO
# - conditionally skip all tests for non-debian systems
# - teste _parse_version_deps_from_pkg_mgr_output deeply

generated_commands = []


@pytest.fixture
def catch_generated_commands(monkeypatch):
    generated_commands[:] = []

    def _f(command, *args, **kwargs):
        generated_commands.append(command)
        return ''

    monkeypatch.setattr(NodeControlUtil, 'run_shell_script', _f)
    monkeypatch.setattr(NodeControlUtil, 'run_shell_script_extended', _f)
    monkeypatch.setattr(NodeControlUtil, 'run_shell_command', _f)


def test_generated_cmd_get_curr_info(catch_generated_commands):
    pkg_name = 'some_package'
    # TODO not an API for now
    NodeControlUtil._get_curr_info(pkg_name)
    assert len(generated_commands) == 1
    assert generated_commands[0] == "dpkg -s {}".format(pkg_name)


def test_generated_cmd_get_latest_pkg_version(catch_generated_commands):
    pkg_name = 'some_package'
    NodeControlUtil.get_latest_pkg_version(pkg_name)
    assert len(generated_commands) == 2
    assert generated_commands[0] == "apt update"
    assert generated_commands[1] == (
        "apt-cache show {} | grep -E '^Version: '"
        .format(pkg_name)
    )

    generated_commands[:] = []
    upstream = src_version_cls(pkg_name)('1.2.3')
    NodeControlUtil.get_latest_pkg_version(
        pkg_name, upstream=upstream, update_cache=False)
    assert len(generated_commands) == 1
    assert generated_commands[0] == (
        "apt-cache show {} | grep -E '^Version: '"
        .format(pkg_name)
    )


def test_generated_cmd_get_info_from_package_manager(catch_generated_commands):
    packages = ['package1', 'package2']
    # TODO not an API for now
    NodeControlUtil._get_info_from_package_manager(*packages)
    assert len(generated_commands) == 1
    assert generated_commands[0] == "apt-cache show {}".format(" ".join(packages))


def test_generated_cmd_update_package_cache(catch_generated_commands):
    NodeControlUtil.update_package_cache()
    assert len(generated_commands) == 1
    assert generated_commands[0] == "apt update"


def test_generated_cmd_get_sys_holds(monkeypatch, catch_generated_commands):
    monkeypatch.setattr(shutil, 'which', lambda *_: 'path')
    NodeControlUtil.get_sys_holds()
    assert len(generated_commands) == 1
    assert generated_commands[0] == "apt-mark showhold"


def test_generated_cmd_hold_packages(monkeypatch, catch_generated_commands):
    packages = ['package1', 'package2']
    monkeypatch.setattr(shutil, 'which', lambda *_: 'path')
    NodeControlUtil.hold_packages(packages)
    assert len(generated_commands) == 1
    assert generated_commands[0] == "apt-mark hold {}".format(' '.join(packages))


def test_get_latest_pkg_version_invalid_args():
    pkg_name = 'any_package'
    with pytest.raises(TypeError) as excinfo:
        NodeControlUtil.get_latest_pkg_version(
            pkg_name,
            upstream=DigitDotVersion('1.2.3'),
            update_cache=False
        )
    assert (
        "should be instance of {}"
        .format(src_version_cls(pkg_name)) in str(excinfo.value)
    )


@pytest.mark.parametrize(
    'pkg_name,upstream,output,expected',
    [
        # some top level package
        ('any_package', None, '', None),
        ('any_package', None, 'Version: 1.2.3\nVersion: 1.2.4', '1.2.4'),
        ('any_package', None, 'Version: 1.2.4\nVersion: 1.2.3', '1.2.4'),
        # self package (APP_NAME)
        (APP_NAME, None, 'Version: 1.2.3\nVersion: 1.2.4', '1.2.4'),
        (APP_NAME, None, 'Version: 1.2.4\nVersion: 1.2.3', '1.2.4'),
        (APP_NAME, None, 'Version: 1.2.4~dev1\nVersion: 1.2.4~rc1', '1.2.4rc1'),
        (APP_NAME, None, 'Version: 1.2.4~rc1\nVersion: 1.2.4~dev1', '1.2.4rc1'),
        (APP_NAME, None, 'Version: 1.2.4~dev1\nVersion: 1.2.4', '1.2.4'),
        (APP_NAME, None, 'Version: 1.2.4~rc2\nVersion: 1.2.4', '1.2.4'),
        (APP_NAME, '1.2.5', 'Version: 1.2.4', None),
        (APP_NAME, '1.2.5', 'Version: 1.2.5~rc1', None),
        (APP_NAME, '1.2.5', 'Version: 1.2.5~dev1', None),
        # invalid versions from output
        ('any_package', None, 'Version: 1.2.3.4.5', None),
        (APP_NAME, None, 'Version: 1.2.3.4.5', None),
        # combined cases
        ('any_package', None, 'Version: 1.2.3\nVersion: 1.2.4\nVersion: 1.2.3.4.5', '1.2.4'),
        ('any_package', '1.2.5', 'Version: 1.2.3\nVersion: 1.2.4\nVersion: 1.2.3.4.5', None),
        (APP_NAME, None, 'Version: 1.2.3\nVersion: 1.2.4\nVersion: 1.2.5~rc1\nVersion: 1.2.5~dev1\nVersion: 1.2.3.4.5', '1.2.5rc1'),
        (APP_NAME, '1.2.5', 'Version: 1.2.3\nVersion: 1.2.4\nVersion: 1.2.5~rc1\nVersion: 1.2.5~dev1\nVersion: 1.2.3.4.5', None),
    ],
    ids=lambda s: s.replace('\n', '_').replace(' ', '_')
)
def test_get_latest_pkg_version(
        monkeypatch, pkg_name, upstream, output, expected):

    def _f(command, *args, **kwargs):
        if not output:
            raise ShellError(1, command)
        else:
            return output

    if upstream is not None:
        upstream = src_version_cls(pkg_name)(upstream)

    expected = None if expected is None else src_version_cls(pkg_name)(expected)

    monkeypatch.setattr(NodeControlUtil, 'run_shell_script_extended', _f)
    res = NodeControlUtil.get_latest_pkg_version(
        pkg_name, upstream, update_cache=False)
    assert expected == res if expected is None else res.upstream


def test_get_latest_pkg_version_for_unknown_package():
    assert NodeControlUtil.get_latest_pkg_version(
        'some-unknown-package-name', update_cache=False) is None


def test_curr_pkg_info_no_data(monkeypatch):
    monkeypatch.setattr(NodeControlUtil, 'run_shell_command', lambda *_: '')
    assert (None, []) == NodeControlUtil.curr_pkg_info('any_package')


def test_curr_pkg_info(monkeypatch):
    output = 'Version: 1.2.3\nDepends: aaa (= 1.2.4), bbb (>= 1.2.5), ccc, aaa'
    expected_deps = ['aaa=1.2.4', 'bbb=1.2.5', 'ccc']
    monkeypatch.setattr(NodeControlUtil, 'run_shell_command', lambda *_: output)

    for pkg_name in [APP_NAME, 'any_package']:
        upstream_cls = src_version_cls(pkg_name)
        expected_version = DebianVersion(
            '1.2.3', upstream_cls=upstream_cls)

        pkg_info = NodeControlUtil.curr_pkg_info(pkg_name)

        assert expected_version == pkg_info[0]
        assert isinstance(expected_version, type(pkg_info[0]))
        assert isinstance(expected_version.upstream, type(pkg_info[0].upstream))
        assert expected_deps == pkg_info[1]
