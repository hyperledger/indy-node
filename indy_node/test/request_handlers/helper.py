import random

from plenum.common.exceptions import UnauthorizedClientRequest
from plenum.common.txn_util import get_seq_no
from plenum.common.util import randomString
from plenum.test.testing_utils import FakeSomething


def add_to_idr(idr, identifier, role):
    random_s = randomString()
    idr.set(identifier,
            seqNo=5,
            txnTime=random.randint(10, 100000),
            ta=random_s,
            role=role,
            verkey=random_s,
            isCommitted=True)


def get_fake_ledger():
    ledger = FakeSomething()
    ledger.txn_list = {}
    ledger.getBySeqNo = lambda seq_no: ledger.txn_list[seq_no]
    ledger.appendTxns = lambda txns: ledger.txn_list.update({get_seq_no(txn): txn
                                                             for txn in txns})
    return ledger


def get_exception(is_exception):
    def exception(request, action_list):
        if is_exception:
            raise UnauthorizedClientRequest(None, None)
        else:
            pass

    return exception
