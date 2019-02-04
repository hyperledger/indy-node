import dateutil

from indy_node.server.restart_log import RestartLog
from datetime import datetime
import os
from os import path


tmpDir = "/tmp/indy/"
tmpFileName = "restart_log_test_file"


def test_restart_log():
    """
    Test for RestartLog class.
    Adds record to it, gets it back and compares.
    Then opens the same file file another instance and tries to
    read added record
    """
    tmpFilePath = path.join(tmpDir, tmpFileName)
    if not os.path.exists(tmpDir):
        os.makedirs(tmpDir)
    elif os.path.exists(tmpFilePath):
        os.remove(tmpFilePath)
    log = RestartLog(tmpFilePath)
    assert log.lastEvent is None

    now = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())

    # Check that we can add and then get event
    log.appendScheduled(now)
    last = log.lastEvent
    assert last[1] is RestartLog.SCHEDULED
    assert last[2] == now

    # Check that the we can load and parse the line we appended before
    assert RestartLog(tmpFilePath).lastEvent == last
