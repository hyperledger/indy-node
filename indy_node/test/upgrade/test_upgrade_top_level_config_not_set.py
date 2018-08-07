import pytest
from indy_node.test.upgrade.helper import NodeControlToolExecutor as NCT, \
    nodeControlGeneralMonkeypatching


@pytest.fixture(scope="module")
def tconf(tconf):
    oldv = tconf.UPGRADE_ENTRY
    tconf.UPGRADE_ENTRY = None
    yield tconf
    tconf.UPGRADE_ENTRY = oldv


def test_upg_invalid_cfg(tdir, monkeypatch, tconf):
    def transform(tool):
        nodeControlGeneralMonkeypatching(tool, monkeypatch, tdir, "")

    with pytest.raises(AssertionError) as ex:
        NCT(backup_dir=tdir, backup_target=tdir, transform=transform)
    assert "UPGRADE_ENTRY config parameter must be set" in str(ex.value)
