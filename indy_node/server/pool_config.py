from plenum.common.constants import TXN_TYPE
from indy_common.constants import POOL_CONFIG, WRITES

from stp_core.common.log import getlogger

logger = getlogger()


class PoolConfig:
    def __init__(self, ledger):
        self.writes = True
        self.ledger = ledger

    def isWritable(self):
        return self.writes

    def handleConfigTxn(self, txn) -> None:
        """
        Handles transaction of type POOL_CONFIG

        :param txn:
        """
        if txn[TXN_TYPE] == POOL_CONFIG:
            self.writes = txn[WRITES]

    # TODO: config ledger is read from the start to the end. Think about optimization
    # TODO: PoolConfig and Updater both read config ledger independently
    def processLedger(self) -> None:
        """
        Checks ledger config txns and perfomes recent one

        :return:
        """
        logger.debug('{} processing config ledger for any POOL_CONFIGs'.format(
            self), extra={"tags": ["pool-config"]})
        for _, txn in self.ledger.getAllTxn():
            if txn[TXN_TYPE] == POOL_CONFIG:
                self.handleConfigTxn(txn)
