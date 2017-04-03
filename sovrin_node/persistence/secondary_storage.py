from ledger.util import F
from plenum.common.constants import TXN_TYPE
from plenum.persistence.secondary_storage import SecondaryStorage as PlenumSS

from sovrin_common.txn import NYM


class SecondaryStorage(PlenumSS):

    def getReply(self, identifier, reqId, **kwargs):
        txn = self._txnStore.getTxn(identifier, reqId, **kwargs)
        if txn:
            txn.update(self._primaryStorage.merkleInfo(txn.get(F.seqNo.name)))
            return txn

    def getReplies(self, *txnIds, seqNo=None):
        txnData = self._txnStore.getResultForTxnIds(*txnIds, seqNo=seqNo)
        if not txnData:
            return txnData
        else:
            for seqNo in txnData:
                txnData[seqNo].update(self._primaryStorage.merkleInfo(seqNo))
            return txnData

    def getAddNymTxn(self, nym):
        return self._txnStore.getAddNymTxn(nym)

    def getRole(self, nym):
        return self._txnStore.getRole(nym)

    def getSponsorFor(self, nym):
        return self._txnStore.getSponsorFor(nym)

    @staticmethod
    def isAddNymTxn(result):
        return result[TXN_TYPE] == NYM

    def hasNym(self, nym) -> bool:
        return self._txnStore.hasNym(nym)

    def countStewards(self) -> int:
        return self._txnStore.countStewards()

    def isSteward(self, nym):
        return self._txnStore.hasSteward(nym)
