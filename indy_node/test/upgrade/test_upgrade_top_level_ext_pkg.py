import pytest
from indy_node.test.upgrade.helper import NodeControlToolExecutor as NCT, \
    nodeControlGeneralMonkeypatching
from indy_node.utils.node_control_tool import DEPS, PACKAGES_TO_HOLD


EXT_PKT_VERSION = '7.88.999'
EXT_PKT_NAME = 'SomeTopLevelPkt'
EXT_PKT_DEPS = ['aa0', 'bb1', 'cc2', 'dd3', 'ee4', 'ff5', 'gg6', 'hh7']
PACKAGE_MNG_EXT_PTK_OUTPUT = "Package: {}\nStatus: install ok installed\nPriority: extra\nSection: default\n" \
                             "Installed-Size: 21\nMaintainer: EXT_PKT_NAME-fond\nArchitecture: amd64\nVersion: {}\n" \
                             "Depends: {}, {} (= 1.1.1), {} (< 1.1.1), {} (<= 1.1.1), {} (> 1.1.1), {} (>= 1.1.1)," \
                             " {} (<< 1.1.1), {} (>> 1.1.1)\nDescription: EXT_PKT_DEPS-desc\n" \
                             "License: EXT_PKT_DEPS-lic\nVendor: none\n".\
    format(EXT_PKT_NAME, EXT_PKT_VERSION, EXT_PKT_DEPS[0], EXT_PKT_DEPS[1], EXT_PKT_DEPS[2],
           EXT_PKT_DEPS[3], EXT_PKT_DEPS[4], EXT_PKT_DEPS[5], EXT_PKT_DEPS[6], EXT_PKT_DEPS[7])


@pytest.fixture(scope="module")
def tconf(tconf):
    oldv = tconf.UPGRADE_ENTRY
    tconf.UPGRADE_ENTRY = EXT_PKT_NAME
    yield tconf
    tconf.UPGRADE_ENTRY = oldv


def test_upg_ext_info(tdir, monkeypatch, tconf):
    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, PACKAGE_MNG_EXT_PTK_OUTPUT)

    nct = NCT(backup_dir=tdir, backup_target=tdir, transform=transform)
    try:
        assert EXT_PKT_VERSION, EXT_PKT_DEPS == nct.tool._ext_info()
        nct.tool._ext_init()
        assert nct.tool.ext_ver == EXT_PKT_VERSION
        assert nct.tool.deps == EXT_PKT_DEPS + DEPS
        hlds = list(set([EXT_PKT_NAME] + EXT_PKT_DEPS + PACKAGES_TO_HOLD.strip(" ").split(" "))).sort()
        cmp_with = list(set(nct.tool.packages_to_hold.strip(" ").split(" "))).sort()
        assert cmp_with == hlds
    finally:
        nct.stop()
