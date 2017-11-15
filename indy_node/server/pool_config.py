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
