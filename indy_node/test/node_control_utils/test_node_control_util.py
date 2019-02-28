import pytest
import shutil


from indy_node.utils.node_control_utils import NodeControlUtil, ShellException

generated_command = None

# TODO
# - conditionally skip all tests for non-debian systems


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

    upstream_version = '1.2.3'
    NodeControlUtil.get_latest_pkg_version(pkg_name, upstream=upstream_version)
    assert generated_command == (
        "apt-cache show {} | grep -E '^Version: ([0-9]+:)?{}(-|$)'"
        .format(pkg_name, upstream_version)
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


@pytest.mark.parametrize(
    'output,expected',
    [
        ('', None),
        ('Version: 1.2.3\nVersion: 1.2.4', '1.2.4'),
    ],
    ids=lambda s: s.replace('\n', '_').replace(' ', '_')
)
def test_get_latest_pkg_version(monkeypatch, output, expected):
    def _f(command, *args, **kwargs):
        if not output:
            raise ShellException(1, command)
        else:
            return output

    monkeypatch.setattr(NodeControlUtil, 'run_shell_script', _f)
    assert expected == NodeControlUtil.get_latest_pkg_version('any_package')


def test_get_latest_pkg_version_for_unknown_package():
    assert NodeControlUtil.get_latest_pkg_version('some-unknown-package-name') is None
