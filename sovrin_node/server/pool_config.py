from plenum.common.constants import TXN_TYPE
from sovrin_common.constants import POOL_CONFIG, WRITES

import os
from collections import deque
from datetime import datetime, timedelta
from functools import cmp_to_key
from functools import partial
from typing import Tuple, Union, Optional

import dateutil.parser
import dateutil.tz

from stp_core.common.log import getlogger
from plenum.common.constants import NAME, TXN_TYPE
from plenum.common.constants import VERSION
from plenum.server.has_action_queue import HasActionQueue
from sovrin_common.constants import ACTION, POOL_UPGRADE, START, SCHEDULE, \
    CANCEL, JUSTIFICATION, TIMEOUT
from sovrin_node.server.upgrade_log import UpgradeLog
from plenum.server import notifier_plugin_manager
import asyncio


logger = getlogger()

class PoolConfig:
    def __init__(self, ledger):
        self.writes = None
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

    def processLedger(self) -> None:
        """
        Checks ledger config txns and perfomes recent one

        :return:
        """
        logger.info('{} processing config ledger for any POOL_CONFIGs'.format(self), extra={"tags": ["pool-config"]})
        for _, txn in self.ledger.getAllTxn():
            if txn[TXN_TYPE] == POOL_CONFIG:
                self.handleConfigTxn(txn)