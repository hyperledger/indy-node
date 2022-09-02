from ast import arg
import pytest
import shutil
import re

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


some_package_info = 'Package: some_package\nVersion: 1.2.3\nDepends: aaa (= 1.2.4), bbb (>= 1.2.5), ccc, aaa'
some_other_package_info = 'Package: some_other_package\nVersion: 4.5.6\nDepends: ddd (= 3.4.5), eee (>= 5.1.2), fff, ddd'
app_package_info = f'Package: {APP_NAME}\nVersion: 1.2.3\nDepends: aaa (= 1.2.4), bbb (>= 1.2.5), ccc, aaa'
any_package_info = 'Package: any_package\nVersion: 1.2.3\nDepends: aaa (= 1.2.4), bbb (>= 1.2.5), ccc, aaa'

@pytest.fixture
def patch_run_shell_command(monkeypatch):
    generated_commands[:] = []

    pkg_list = f'openssl\nsed\ntar\nsome_package\nsome_other_package\n{APP_NAME}\nany_package'
    pkg_info = f'{some_package_info}\n\n{some_other_package_info}\n\n{app_package_info}\n\n{any_package_info}'

    def mock_run_shell_command(command, *args, **kwargs):
        # Keep track of the generated commands
        generated_commands.append(command)
        if command == 'dpkg --get-selections | grep -v deinstall | cut -f1':
            return pkg_list
        else:
            package_name = command.split()[-1]
            packages = re.split("\n\n", pkg_info)
            for package in packages:
                if package_name in package:
                    return package

            return ''

    monkeypatch.setattr(NodeControlUtil, 'run_shell_command', mock_run_shell_command)


@pytest.mark.parametrize(
    'pkg_name',
    [
        pytest.param('not_installed_package', id='not_installed_package'),
        # Ensure partial matches don't work.
        pytest.param('some', id='partial_name_match-some'),
        pytest.param('package', id='partial_name_match-package'),
    ]
)
def test_generated_cmd_get_curr_info_pkg_not_installed(patch_run_shell_command, pkg_name):
    pkg_name = 'not_installed_package'
    # TODO not an API for now
    NodeControlUtil._get_curr_info(pkg_name)
    assert len(generated_commands) == 1
    assert generated_commands[0] == 'dpkg --get-selections | grep -v deinstall | cut -f1'


def test_generated_cmd_get_curr_info_pkg_installed(patch_run_shell_command):
    pkg_name = 'some_package'
    # TODO not an API for now
    NodeControlUtil._get_curr_info(pkg_name)
    assert len(generated_commands) == 2
    assert generated_commands[0] == 'dpkg --get-selections | grep -v deinstall | cut -f1'
    assert generated_commands[1] == "dpkg -s {}".format(pkg_name)


def test_generated_cmd_get_curr_info_accepts_single_pkg_only(patch_run_shell_command):
    expected_pkg_name = 'some_other_package'
    # The extra spaces between the package names is on purpose.
    pkg_name = 'some_other_package   some_package'
    # TODO not an API for now
    NodeControlUtil._get_curr_info(pkg_name)
    assert len(generated_commands) == 2
    assert generated_commands[0] == 'dpkg --get-selections | grep -v deinstall | cut -f1'
    assert generated_commands[1] == "dpkg -s {}".format(expected_pkg_name)


@pytest.mark.parametrize(
    'pkg_name,package',
    [
        pytest.param('some_package', 'some_package|echo "hey";echo "hi"&&echo "hello"|echo "hello world"\necho "hello world!"', id='strips mixed cmd concat'),
        pytest.param('some_package', 'some_package|echo "hey"', id='strips pipe cmd concat'),
        pytest.param('some_package', 'some_package;echo "hey"', id='strips semi-colon cmd concat'),
        pytest.param('some_package', 'some_package&&echo "hey"', id='strips AND cmd concat'),
        pytest.param('some_package', 'some_package\necho "hey"', id='strips Cr cmd concat'),
        pytest.param('some_package', 'some_package echo "hey"', id='strips whitespace'),
    ]
)
def test_generated_cmd_get_curr_info_with_command_concat(patch_run_shell_command, pkg_name, package):
    # TODO not an API for now
    NodeControlUtil._get_curr_info(package)
    assert len(generated_commands) == 2
    assert generated_commands[0] == 'dpkg --get-selections | grep -v deinstall | cut -f1'
    assert generated_commands[1] == "dpkg -s {}".format(pkg_name)


@pytest.mark.parametrize(
    'pkg_name,expected_output',
    [
        pytest.param('some_package', some_package_info, id='some_package'),
        pytest.param('some_other_package', some_other_package_info, id='some_other_package'),
        pytest.param(APP_NAME, app_package_info, id=APP_NAME),
        pytest.param('any_package', any_package_info, id='any_package'),
        pytest.param('not_installed_package', '', id='not_installed_package'),
        # Ensure partial matches don't work.
        pytest.param('some', '', id='partial_name_match-some'),
        pytest.param('package', '', id='partial_name_match-package'),
    ]
)
def test_get_curr_info_output(patch_run_shell_command, pkg_name, expected_output):
    pkg_info = NodeControlUtil._get_curr_info(pkg_name)
    assert pkg_info == expected_output


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

# apt update is successful
def test_generated_cmd_update_package_cache(catch_generated_commands):
    NodeControlUtil.update_package_cache()
    assert len(generated_commands) == 1
    assert generated_commands[0] == "apt update"

# apt update fails
# apt update dependencies don't need to be upgraded, i.e. only key update is performed.
def test_generated_cmd_update_package_cache_2(monkeypatch):
    run_shell_script_counter = 0
    commands = []

    def _run_shell_script(command, *args, **kwargs):
        nonlocal run_shell_script_counter
        run_shell_script_counter += 1
        commands.append(command)

        if run_shell_script_counter == 1:
            raise Exception("Command 'apt update' returned non-zero exit status")

        return ''

    def _f(command, *args, **kwargs):
        commands.append(command)
        return ''

    monkeypatch.setattr(NodeControlUtil, 'run_shell_script', _run_shell_script)
    monkeypatch.setattr(NodeControlUtil, 'run_shell_script_extended', _f)
    monkeypatch.setattr(NodeControlUtil, 'run_shell_command', _f)

    NodeControlUtil.update_package_cache()
    assert len(commands) == 4
    assert commands[0] == "apt update"
    assert commands[1] == "apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88"
    assert commands[2] == "apt list --upgradable"
    assert commands[3] == "apt update"


# apt update fails
# apt update dependencies need to be upgraded
def test_generated_cmd_update_package_cache_3(monkeypatch):
    run_shell_script_counter = 0
    commands = []

    def _run_shell_script(command, *args, **kwargs):
        nonlocal run_shell_script_counter
        run_shell_script_counter += 1
        commands.append(command)

        if run_shell_script_counter == 1:
            raise Exception("Command 'apt update' returned non-zero exit status")

        return ''

    def _run_shell_command(command, *args, **kwargs):
        commands.append(command)
        return """libgnutls-openssl27/xenial-updates 3.4.10-4ubuntu1.9 amd64 [upgradable from: 3.4.10-4ubuntu1.7]
libgnutls30/xenial-updates 3.4.10-4ubuntu1.9 amd64 [upgradable from: 3.4.10-4ubuntu1.7]
liblxc1/xenial-updates 2.0.11-0ubuntu1~16.04.3 amd64 [upgradable from: 2.0.8-0ubuntu1~16.04.2]"""

    def _f(command, *args, **kwargs):
        commands.append(command)
        return ''

    monkeypatch.setattr(NodeControlUtil, 'run_shell_script', _run_shell_script)
    monkeypatch.setattr(NodeControlUtil, 'run_shell_script_extended', _f)
    monkeypatch.setattr(NodeControlUtil, 'run_shell_command', _run_shell_command)

    NodeControlUtil.update_package_cache()
    assert len(commands) == 5
    assert commands[0] == "apt update"
    assert commands[1] == "apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88"
    assert commands[2] == "apt list --upgradable"
    assert commands[3] == "apt --only-upgrade install -y libgnutls30"
    assert commands[4] == "apt update"


def test_generated_cmd_update_repo_keys(catch_generated_commands):
    NodeControlUtil.update_repo_keys()
    assert len(generated_commands) == 1
    assert generated_commands[0] == "apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88"


# apt update dependencies don't need to be upgraded
def test_generated_cmd_update_apt_update_dependencies_1(catch_generated_commands):
    NodeControlUtil.update_apt_update_dependencies()
    assert len(generated_commands) == 1
    assert generated_commands[0] == "apt list --upgradable"


# apt update dependencies need to be upgraded
def test_generated_cmd_update_apt_update_dependencies_2(monkeypatch):
    commands = []

    def _run_shell_command(command, *args, **kwargs):
        commands.append(command)
        return """libgnutls-openssl27/xenial-updates 3.4.10-4ubuntu1.9 amd64 [upgradable from: 3.4.10-4ubuntu1.7]
libgnutls30/xenial-updates 3.4.10-4ubuntu1.9 amd64 [upgradable from: 3.4.10-4ubuntu1.7]
liblxc1/xenial-updates 2.0.11-0ubuntu1~16.04.3 amd64 [upgradable from: 2.0.8-0ubuntu1~16.04.2]"""

    def _f(command, *args, **kwargs):
        commands.append(command)
        return ''

    monkeypatch.setattr(NodeControlUtil, 'run_shell_script', _f)
    monkeypatch.setattr(NodeControlUtil, 'run_shell_script_extended', _f)
    monkeypatch.setattr(NodeControlUtil, 'run_shell_command', _run_shell_command)

    NodeControlUtil.update_apt_update_dependencies()
    assert len(commands) == 2
    assert commands[0] == "apt list --upgradable"
    assert commands[1] == "apt --only-upgrade install -y libgnutls30"


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
    ids=lambda s: s.replace('\n', '_').replace(' ', '_') if s else None
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


def test_curr_pkg_info_no_data(patch_run_shell_command):
    assert (None, []) == NodeControlUtil.curr_pkg_info('some-unknown-package-name')


@pytest.mark.parametrize(
    'pkg_name,version,expected_deps',
    [
        pytest.param('some_package', '1.2.3', ['aaa=1.2.4', 'bbb=1.2.5', 'ccc'], id='some_package'),
        pytest.param('some_other_package', '4.5.6', ['ddd=3.4.5', 'eee=5.1.2', 'fff'], id='some_other_package'),
        pytest.param(APP_NAME, '1.2.3', ['aaa=1.2.4', 'bbb=1.2.5', 'ccc'], id=APP_NAME),
        pytest.param('any_package', '1.2.3', ['aaa=1.2.4', 'bbb=1.2.5', 'ccc'], id='any_package'),
    ]
)
def test_curr_pkg_info(patch_run_shell_command, pkg_name, version, expected_deps):
    upstream_cls = src_version_cls(pkg_name)
    expected_version = DebianVersion(
        version, upstream_cls=upstream_cls)

    pkg_info = NodeControlUtil.curr_pkg_info(pkg_name)

    assert expected_version == pkg_info[0]
    assert isinstance(expected_version, type(pkg_info[0]))
    assert isinstance(expected_version.upstream, type(pkg_info[0].upstream))
    assert expected_deps == pkg_info[1]


@pytest.mark.parametrize(
    'pkg_name',
    [
        pytest.param(f'{APP_NAME} | echo "hey"; echo "hi" && echo "hello"|echo "hello world"', id='multiple'),
        pytest.param(f'{APP_NAME}|echo "hey"', id='pipe'),
        pytest.param(f'{APP_NAME};echo "hey"', id='semi-colon'),
        pytest.param(f'{APP_NAME}&&echo "hey"', id='and'),
        pytest.param(f'{APP_NAME}\necho "hey"', id='Cr'),
        pytest.param(f'{APP_NAME} echo "hey"', id='whitespace'),
    ]
)
def test_curr_pkg_info_with_command_concat(patch_run_shell_command, pkg_name):
    expected_deps = ['aaa=1.2.4', 'bbb=1.2.5', 'ccc']
    upstream_cls = src_version_cls(pkg_name)
    expected_version = DebianVersion(
        '1.2.3', upstream_cls=upstream_cls)

    pkg_info = NodeControlUtil.curr_pkg_info(pkg_name)

    assert expected_version == pkg_info[0]
    assert isinstance(expected_version, type(pkg_info[0]))
    assert isinstance(expected_version.upstream, type(pkg_info[0].upstream))
    assert expected_deps == pkg_info[1]