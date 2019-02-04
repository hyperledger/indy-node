from indy_common.constants import POOL_CONFIG, WRITES
from plenum.common.txn_util import get_type, get_payload_data

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
        if get_type(txn) == POOL_CONFIG:
            self.writes = get_payload_data(txn)[WRITES]

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
            if get_type(txn) == POOL_CONFIG:
                self.handleConfigTxn(txn)
