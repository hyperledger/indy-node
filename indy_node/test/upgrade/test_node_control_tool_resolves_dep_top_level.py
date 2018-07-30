import pytest
from indy_node.utils.node_control_tool import NodeControlTool
from plenum.test.helper import randomText


EXT_PKT_VERSION = '7.88.999'
EXT_PKT_NAME = 'SomeTopLevelPkt'
node_package = ('indy-node', '0.0.1')
PACKAGE_MNG_EXT_PTK_OUTPUT = "Package: {}\nStatus: install ok installed\nPriority: extra\nSection: default\n" \
                             "Installed-Size: 21\nMaintainer: EXT_PKT_NAME-fond\nArchitecture: amd64\nVersion: {}\n" \
                             "Depends: {}\nDescription: EXT_PKT_DEPS-desc\n" \
                             "License: EXT_PKT_DEPS-lic\nVendor: none\n".\
    format(EXT_PKT_NAME, EXT_PKT_VERSION, "indy-node")


@pytest.fixture(scope="module")
def tconf(tconf):
    oldv = tconf.UPGRADE_ENTRY
    tconf.UPGRADE_ENTRY = EXT_PKT_NAME
    yield tconf
    tconf.UPGRADE_ENTRY = oldv


def test_node_as_depend(monkeypatch, tconf):
    nct = NodeControlTool(config=tconf)
    top_level_package = (EXT_PKT_NAME, EXT_PKT_VERSION)
    anoncreds_package = ('indy-anoncreds', '0.0.2')
    plenum_package = ('indy-plenum', '0.0.3')
    top_level_package_with_version = '{}={}'.format(*top_level_package)
    node_package_with_version = '{}={}'.format(*node_package)
    plenum_package_with_version = '{}={}'.format(*plenum_package)
    anoncreds_package_with_version = '{}={}'.format(*anoncreds_package)
    mock_info = {
        top_level_package_with_version: "{}{} (= {})".format(randomText(100), *node_package),
        node_package_with_version: '{}{} (= {}){}{} (= {}){}'.format(randomText(100), *plenum_package, randomText(100),
                                                                     *anoncreds_package, randomText(100)),
        plenum_package_with_version: '{}'.format(randomText(100)),
        anoncreds_package_with_version: '{}'.format(randomText(100))
    }

    def mock_get_info_from_package_manager(self, package):
        return mock_info.get(package, None)

    monkeypatch.setattr(nct.__class__, '_get_ext_info', lambda *x: PACKAGE_MNG_EXT_PTK_OUTPUT)
    monkeypatch.setattr(nct.__class__, '_get_info_from_package_manager', mock_get_info_from_package_manager)
    monkeypatch.setattr(nct.__class__, '_update_package_cache', lambda *x: None)
    nct._ext_init()
    ret = nct._get_deps_list(top_level_package_with_version)
    assert ret.split() == [
        anoncreds_package_with_version,
        plenum_package_with_version,
        node_package_with_version,
        top_level_package_with_version]