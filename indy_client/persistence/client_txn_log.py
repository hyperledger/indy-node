from typing import List

from plenum.common.constants import TXN_TYPE
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
            if txn.get(TXN_TYPE) == txnType:
                txns.append(txn)
        return txns
