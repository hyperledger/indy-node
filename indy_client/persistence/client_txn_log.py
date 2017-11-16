#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

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
