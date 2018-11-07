from typing import List

from plenum.common.txn_util import get_type
from plenum.common.util import updateFieldsWithSeqNo
from plenum.persistence.client_txn_log import ClientTxnLog as PClientTxnLog

from indy_common.txn_util import getTxnOrderedFields


class ClientTxnLog(PClientTxnLog):

    @property
    def txnFieldOrdering(self):
        fields = getTxnOrderedFields()
        return updateFieldsWithSeqNo(fields)

    def getTxnsByType(self, txnType: str) -> List:
        txns = []
        for val in self.transactionLog.iterator(include_key=False,
                                                include_value=True):
            txn = self.serializer.deserialize(
                val, fields=self.txnFieldOrdering)
            if get_type(txn) == txnType:
                txns.append(txn)
        return txns
