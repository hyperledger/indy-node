from sovrin_node.server.upgrade_log import UpgradeLog
from datetime import datetime
import os
from os import path


tmpDir = "/tmp/sovrin/"
tmpFileName = "upgrade_log_test_file"


def test_update_log():
    """
    Test for UpgradeLog class.
    Adds record to it, gets it back and compares.
    Then opens the same file file another instance and tries to
    read added record
    """
    tmpFilePath = path.join(tmpDir, tmpFileName)
    if not os.path.exists(tmpDir):
        os.makedirs(tmpDir)
    elif os.path.exists(tmpFilePath):
        os.remove(tmpFilePath)
    log = UpgradeLog(tmpFilePath)
    assert log.lastEvent is None

    now = datetime.utcnow()
    version = "1.2.3"

    # Check that we can add and then get event
    log.appendScheduled(now, version)
    last = log.lastEvent
    assert last[1] is UpgradeLog.UPGRADE_SCHEDULED
    assert last[2] == now
    assert last[3] == version

    # Check that the we can load and parse the line we appended before
    assert UpgradeLog(tmpFilePath).lastEvent == last
