import pytest

from common.version import InvalidVersionError
from plenum.common.exceptions import BlowUp

from indy_common.constants import APP_NAME
from indy_common.version import src_version_cls

from indy_node.test.upgrade.helper import (
    NodeControlToolPatched,
    composeUpgradeMessage
)


@pytest.fixture(scope='module')
def tconf(tconf, tdir):
    tconf.LOG_DIR = tdir
    yield tconf


def test_node_control_tool_processes_invalid_json(
    monkeypatch, tdir, tconf
):
    def patch(tool):
        monkeypatch.setattr(tool, '_listen', lambda *x, **y: None)
        monkeypatch.setattr(tool, '_upgrade', lambda *x, **y: None)
        monkeypatch.setattr(tool, '_restart', lambda *x, **y: None)

    tool = NodeControlToolPatched(patch, backup_dir=tdir, backup_target=tdir, config=tconf)

    with pytest.raises(BlowUp, match='JSON decoding failed'):
        tool._process_data('{12345}'.encode('utf-8'))


@pytest.mark.parametrize(
    'pkg_name,version',
    [
        ('some-pkg', '1.2.3.4.5'),
        (APP_NAME, '1.2.3.4.5'),
    ]
)
def test_node_control_tool_processes_invalid_version(
    monkeypatch, tdir, tconf, pkg_name, version
):
    def patch(tool):
        monkeypatch.setattr(tool, '_listen', lambda *x, **y: None)
        monkeypatch.setattr(tool, '_upgrade', lambda *x, **y: None)
        monkeypatch.setattr(tool, '_restart', lambda *x, **y: None)

    tool = NodeControlToolPatched(patch, backup_dir=tdir, backup_target=tdir, config=tconf)

    with pytest.raises(InvalidVersionError):
        src_version_cls(pkg_name)(version)

    with pytest.raises(BlowUp, match='invalid version 1.2.3.4.5'):
        tool._process_data(composeUpgradeMessage(version, pkg_name))
