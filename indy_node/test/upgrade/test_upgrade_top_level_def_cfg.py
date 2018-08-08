from indy_node.test.upgrade.helper import NodeControlToolExecutor as NCT, \
    nodeControlGeneralMonkeypatching
from indy_node.utils.node_control_tool import DEPS, PACKAGES_TO_HOLD


def test_upg_default_cfg(tdir, monkeypatch, tconf):
    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, "")

    nct = NCT(backup_dir=tdir, backup_target=tdir, transform=transform)
    try:
        assert nct.tool.ext_ver is None
        assert nct.tool.deps == DEPS
        assert nct.tool.packages_to_hold.strip(" ") == PACKAGES_TO_HOLD.strip(" ")
    finally:
        nct.stop()
