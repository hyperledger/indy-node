import pytest

from operator import itemgetter
from indy_common.util import getIndex
from indy_common.util import compose_cmd


def test_getIndex():
    items = [('a', {'key1': 1}), ('b', {'key2': 2})]
    getDict = itemgetter(1)

    def containsKey(key):
        return lambda x: key in getDict(x)

    assert 0 == getIndex(containsKey('key1'), items)
    assert 1 == getIndex(containsKey('key2'), items)
    assert -1 == getIndex(containsKey('key3'), items)


@pytest.mark.parametrize(
    'pkg_name,package',
    [
        pytest.param('some_package', 'some_package', id='some_package'),
        pytest.param('package_1', 'package_1;echo "hi"&&echo "hello"\necho "hello world!"', id='strips mixed cmd concat'),
        pytest.param('package_3', 'package_3;echo "hey"', id='strips semi-colon cmd concat'),
        pytest.param('package_4', 'package_4&&echo "hey"', id='strips and cmd concat'),
        pytest.param('package_5', 'package_5\necho "hey"', id='strips Cr cmd concat'),
    ]
)
def test_compose_cmd(pkg_name, package):
    expected_cmd = f'dpkg -s {pkg_name}'

    cmd = compose_cmd(['dpkg', '-s', package])
    assert expected_cmd == cmd


def test_compose_cmd_allows_whitespace():
    pkg_name = 'package_7 some_other_package'
    expected_cmd = f'dpkg -s {pkg_name}'
    cmd = compose_cmd(['dpkg', '-s', pkg_name])
    assert expected_cmd == cmd


def test_compose_cmd_allows_pipe():
    expected_cmd = 'dpkg --get-selections | grep -v deinstall | cut -f1'
    cmd = compose_cmd(
        ['dpkg', '--get-selections', '|', 'grep', '-v', 'deinstall', '|', 'cut', '-f1']
    )
    assert expected_cmd == cmd
