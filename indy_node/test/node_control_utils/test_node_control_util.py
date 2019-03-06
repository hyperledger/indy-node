import pytest
import shutil

from plenum.common.version import DigitDotVersion

from indy_common.constants import APP_NAME
from indy_common.version import src_version_cls
from indy_node.utils.node_control_utils import (
    NodeControlUtil, ShellError, DebianVersion
)

# TODO
# - conditionally skip all tests for non-debian systems
# - teste _parse_version_deps_from_pkg_mgr_output deeply

generated_command = None


@pytest.fixture
def catch_generated_command(monkeypatch):
    global generated_command
    generated_command = None

    def _f(command, *args, **kwargs):
        global generated_command
        generated_command = command
        return ''

    monkeypatch.setattr(NodeControlUtil, 'run_shell_script', _f)
    monkeypatch.setattr(NodeControlUtil, 'run_shell_command', _f)


def test_generated_cmd_get_curr_info(catch_generated_command):
    pkg_name = 'some_package'
    # TODO not an API for now
    NodeControlUtil._get_curr_info(pkg_name)
    assert generated_command == "dpkg -s {}".format(pkg_name)


def test_generated_cmd_get_latest_pkg_version(catch_generated_command):
    pkg_name = 'some_package'
    NodeControlUtil.get_latest_pkg_version(pkg_name)
    assert generated_command == (
        "apt-cache show {} | grep -E '^Version: ([0-9]+:)?{}(-|$)'"
        .format(pkg_name, '.*')
    )

    upstream = src_version_cls(pkg_name)('1.2.3')
    NodeControlUtil.get_latest_pkg_version(pkg_name, upstream=upstream)
    assert generated_command == (
        "apt-cache show {} | grep -E '^Version: ([0-9]+:)?{}(-|$)'"
        .format(pkg_name, upstream)
    )


def test_generated_cmd_get_info_from_package_manager(catch_generated_command):
    packages = ['package1', 'package2']
    # TODO not an API for now
    NodeControlUtil._get_info_from_package_manager(*packages)
    assert generated_command == "apt-cache show {}".format(" ".join(packages))


def test_generated_cmd_update_package_cache(catch_generated_command):
    NodeControlUtil.update_package_cache()
    assert generated_command == "apt update"


def test_generated_cmd_get_sys_holds(monkeypatch, catch_generated_command):
    monkeypatch.setattr(shutil, 'which', lambda *_: 'path')
    NodeControlUtil.get_sys_holds()
    assert generated_command == "apt-mark showhold"


def test_generated_cmd_hold_packages(monkeypatch, catch_generated_command):
    packages = ['package1', 'package2']
    monkeypatch.setattr(shutil, 'which', lambda *_: 'path')
    NodeControlUtil.hold_packages(packages)
    assert generated_command == "apt-mark hold {}".format(' '.join(packages))


def test_get_latest_pkg_version_invalid_args():
    pkg_name = 'any_package'
    with pytest.raises(TypeError) as excinfo:
        NodeControlUtil.get_latest_pkg_version(
            pkg_name,
            upstream=DigitDotVersion('1.2.3')
        )
    assert (
        "should be instance of {}"
        .format(src_version_cls(pkg_name)) in str(excinfo.value)
    )


@pytest.mark.parametrize(
    'output,expected',
    [
        ('', None),
        ('Version: 1.2.3\nVersion: 1.2.4',
            DebianVersion(
                '1.2.4',
                upstream_cls=src_version_cls('any_package'))),
    ],
    ids=lambda s: s.replace('\n', '_').replace(' ', '_')
)
def test_get_latest_pkg_version(monkeypatch, output, expected):
    def _f(command, *args, **kwargs):
        if not output:
            raise ShellError(1, command)
        else:
            return output

    monkeypatch.setattr(NodeControlUtil, 'run_shell_script', _f)
    assert expected == NodeControlUtil.get_latest_pkg_version('any_package')


def test_get_latest_pkg_version_for_unknown_package():
    assert NodeControlUtil.get_latest_pkg_version('some-unknown-package-name') is None


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
