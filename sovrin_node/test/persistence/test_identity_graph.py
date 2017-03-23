import time
from datetime import datetime, timedelta

from ledger.util import F
from plenum.common.constants import TXN_TIME

from sovrin_common.persistence.identity_graph import IdentityGraph


def testMakeResultTxnTimeString():
    oRecordData = {
        F.seqNo.name: 1,
        TXN_TIME: 'some-datetime'
    }
    assert TXN_TIME not in IdentityGraph.makeResult(0, oRecordData)


def testMakeResultTxnTimeDatetime():
    dt = datetime.now()
    oRecordData = {
        F.seqNo.name: 1,
        TXN_TIME: dt
    }
    assert IdentityGraph.makeResult(0, oRecordData)[TXN_TIME] == int(time.mktime(dt.timetuple()))


def testMakeResultTxnTimeDatetimeInvalidPast():
    dt = datetime(1999, 1, 1)
    oRecordData = {
        F.seqNo.name: 1,
        TXN_TIME: dt
    }
    assert TXN_TIME not in IdentityGraph.makeResult(0, oRecordData)


def testMakeResultTxnTimeDatetimeInvalidFuture():
    dt = datetime.now() + timedelta(1)
    oRecordData = {
        F.seqNo.name: 1,
        TXN_TIME: dt
    }
    assert TXN_TIME not in IdentityGraph.makeResult(0, oRecordData)


def testMakeResultTxnTimeNone():
    from datetime import datetime
    dt = datetime.now()
    oRecordData = {
        F.seqNo.name: 1,
    }
    assert TXN_TIME not in IdentityGraph.makeResult(0, oRecordData)
