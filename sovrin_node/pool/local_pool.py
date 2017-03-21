from collections import deque

from plenum.common.raet import initLocalKeep
from plenum.common.test_network_setup import TestNetworkSetup
from plenum.common.txn import TYPE, NODE, NYM
from plenum.common.looper import Looper
from plenum.common.util import adict

from sovrin_common.config_util import getConfig
from sovrin_common.pool.pool import Pool
from sovrin_common.txn import getTxnOrderedFields


class LocalPool(Pool, Looper):

    @property
    def genesis_transactions(self):
        return self.genesis_txns

    def __init__(self, genesis_txns, base_dir, config=None, loop=None):
        super().__init__(loop=loop)
        self.base_dir = base_dir
        self.genesis_txns = genesis_txns
        self.config = config or getConfig(self.base_dir)

    def setup_local_node(self, name, sigseed, override=True):
        _, verkey = initLocalKeep(name, self.base_dir, sigseed, override)

    def generate_genesis_files(self):

        pool_txns, domain_txns = self._split_pool_and_domain()

        # TODO make Ledger a context manager
        pl = TestNetworkSetup.init_pool_ledger(appendToLedgers=False,
                                               baseDir=self.base_dir,
                                               config=self.config,
                                               envName='test')
        pl_lines = self._add_and_stop(pool_txns, pl)

        dl = TestNetworkSetup.init_domain_ledger(appendToLedgers=False,
                                                 baseDir=self.base_dir,
                                                 config=self.config,
                                                 envName='test',
                                                 domainTxnFieldOrder=getTxnOrderedFields())
        dl_lines = self._add_and_stop(domain_txns, dl)

        return adict(pool=adict(lines=pl_lines,
                                root=pl.root_hash,
                                size=pl.size),
                     domain=adict(lines=dl_lines,
                                  root=dl.root_hash,
                                  size=dl.size))

    def _split_pool_and_domain(self):
        pool_txns = deque()
        domain_txns = deque()
        for txn in self.genesis_txns:
            if txn[TYPE] in [NODE]:
                pool_txns.appendleft(txn)
            elif txn[TYPE] in [NYM]:
                domain_txns.appendleft(txn)
            else:
                raise NotImplementedError("txn type '{}' not supported")
        return pool_txns, domain_txns

    @staticmethod
    def _add_and_stop(txns, ledger):
        try:
            while True:
                ledger.add(txns.pop())
        except IndexError:
            pass
        finally:
            ledger.stop()
        with open(ledger._transactionLog.dbPath) as f:
            return f.readlines()