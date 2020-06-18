import pytest

from indy_common.constants import APP_NAME
from indy_node.utils.node_control_tool import NodeControlTool
from plenum.test.helper import randomText
from indy_node.utils.node_control_utils import NodeControlUtil

EXT_PKT_VERSION = '7.88.999'
EXT_PKT_NAME = 'SomeTopLevelPkt'
node_package = (APP_NAME, '0.0.1')
EXT_TOP_PKT_DEPS = [("aa", "1.1.1"), ("bb", "2.2.2")]
PACKAGE_MNG_EXT_PTK_OUTPUT = "Package: {}\nStatus: install ok installed\nPriority: extra\nSection: default\n" \
                             "Installed-Size: 21\nMaintainer: EXT_PKT_NAME-fond\nArchitecture: amd64\nVersion: {}\n" \
                             "Depends: {}, {} (= {}), {} (= {})\nDescription: EXT_PKT_DEPS-desc\n" \
                             "License: EXT_PKT_DEPS-lic\nVendor: none\n". \
    format(EXT_PKT_NAME, EXT_PKT_VERSION, APP_NAME, *EXT_TOP_PKT_DEPS[0], *EXT_TOP_PKT_DEPS[1])


@pytest.fixture(scope="module")
def tconf(tconf, tdir):
    oldv = tconf.UPGRADE_ENTRY
    tconf.UPGRADE_ENTRY = EXT_PKT_NAME
    tconf.LOG_DIR = tdir
    yield tconf
    tconf.UPGRADE_ENTRY = oldv


def test_node_as_depend(monkeypatch, tconf):
    nct = NodeControlTool(config=tconf)
    top_level_package = (EXT_PKT_NAME, EXT_PKT_VERSION)
    plenum_package = ('indy-plenum', '0.0.3')
    top_level_package_with_version = '{}={}'.format(*top_level_package)
    top_level_package_dep1_with_version = '{}={}'.format(*EXT_TOP_PKT_DEPS[0])
    top_level_package_dep2_with_version = '{}={}'.format(*EXT_TOP_PKT_DEPS[1])
    node_package_with_version = '{}={}'.format(*node_package)
    plenum_package_with_version = '{}={}'.format(*plenum_package)
    mock_info = {
        top_level_package_with_version: "{}\nVersion:{}\nDepends:{} (= {}), {} (= {}), {} (= {})\n".format(
            randomText(100), top_level_package[1], *node_package, *EXT_TOP_PKT_DEPS[0], *EXT_TOP_PKT_DEPS[1]),
        node_package_with_version: '{}\nVersion:{}\nDepends:{} (= {})\n'.format(
            randomText(100), node_package[1], *plenum_package),
        plenum_package_with_version: '{}\nVersion:{}\nDepends:{} (= {})\n'.format(
            randomText(100), plenum_package[1], *plenum_package),
        top_level_package_dep1_with_version: '{}\nVersion:{}\nDepends:{} (= {})\n'.format(
            randomText(100), EXT_TOP_PKT_DEPS[0][1], *plenum_package),
        top_level_package_dep2_with_version: '{}\nVersion:{}\nDepends:{} (= {})\n'.format(
            randomText(100), EXT_TOP_PKT_DEPS[1][1], *node_package),
    }

    def mock_get_info_from_package_manager(*package):
        ret = ""
        for p in package:
            ret += mock_info.get(p, "")
        return ret

    monkeypatch.setattr(NodeControlUtil, 'update_package_cache', lambda *x: None)
    monkeypatch.setattr(NodeControlUtil, '_get_info_from_package_manager',
                        lambda *x: mock_get_info_from_package_manager(*x))
    monkeypatch.setattr(NodeControlUtil, 'get_sys_holds',
                        lambda *x: [top_level_package[0], plenum_package[0], node_package[0],
                                    EXT_TOP_PKT_DEPS[0][0], EXT_TOP_PKT_DEPS[1][0]])
    monkeypatch.setattr(NodeControlUtil, '_get_curr_info', lambda *x: PACKAGE_MNG_EXT_PTK_OUTPUT)
    ret = nct._get_deps_list(top_level_package_with_version)
    nct.server.close()
    assert sorted(ret.split()) == sorted([plenum_package_with_version,
                                          node_package_with_version, top_level_package_dep2_with_version,
                                          top_level_package_dep1_with_version, top_level_package_with_version])
