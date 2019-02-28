from indy_node.server.upgrade_log import UpgradeLogData
from datetime import datetime


def test_upgrade_log_data_pack_unpack():
    delimiter = '|'
    data = UpgradeLogData(datetime.utcnow(), '1.2.3', 'some_id', 'some_pkg')
    assert data == UpgradeLogData.unpack(
        data.pack(delimiter=delimiter), delimiter=delimiter
    )
