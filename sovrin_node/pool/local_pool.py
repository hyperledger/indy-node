import os
from collections import deque

import shutil
from plenum.common.member.steward import Steward
from plenum.common.test_network_setup import TestNetworkSetup
from plenum.common.constants import TYPE, NODE, NYM
from plenum.common.util import adict, randomString

from sovrin_client.agent.walleted_agent import WalletedAgent
from sovrin_client.client.client import Client
from sovrin_node.server.node import Node
from sovrin_client.client.wallet.wallet import Wallet

from sovrin_common.config_util import getConfig
from sovrin_common.init_util import initialize_node_environment
from sovrin_common.pool.pool import Pool
from sovrin_common.txn_util import getTxnOrderedFields
from stp_core.crypto.util import randomSeed

from stp_core.loop.looper import Looper


def create_local_pool(base_dir, node_size=4):
    conf = getConfig(base_dir)
    pool_dir = os.path.join(base_dir, "pool")

    # TODO: Need to come back to this why we need this cleanup
    shutil.rmtree(pool_dir, ignore_errors=True)

    stewards = []
    node_conf = []
    nodes = []
    genesis_txns = []
    for i in range(node_size):
        w = Wallet("steward")
        s = Steward(wallet=w)
        s.wallet.addIdentifier()

        stewards.append(s)

        n_config = adict(name='Node' + str(i + 1),
                         basedirpath=pool_dir,
                         ha=('127.0.0.1', 9700 + (i * 2)),
                         cliha=('127.0.0.1', 9700 + (i * 2) + 1))

        n_verkey = initialize_node_environment(name=n_config.name,
                                               base_dir=n_config.basedirpath,
                                               override_keep=True,
                                               config=conf,
                                               sigseed=randomSeed())

        s.set_node(n_config, verkey=n_verkey)

        node_conf.append(n_config)

        genesis_txns += s.generate_genesis_txns()

    pool = LocalPool(genesis_txns, pool_dir, steward=stewards[0])

    for c in node_conf:
        n = Node(**c)
        pool.add(n)
        nodes.append(n)

    pool.runFor(5)

    return pool


class LocalPool(Pool, Looper):
    def __init__(self, genesis_txns, base_dir, config=None,
                 loop=None, steward: Steward=None):
        super().__init__(loop=loop)
        self.base_dir = base_dir
        self.genesis_txns = genesis_txns
        self.config = config or getConfig(self.base_dir)
        self._generate_genesis_files()
        self._steward = steward

        if steward is not None:
            self._steward_agent = WalletedAgent(name="steward1",
                                                basedirpath=self.base_dir,
                                                client=self.create_client(
                                                    5005),
                                                wallet=steward.wallet,
                                                port=8781)
            self.add(self._steward_agent)

    @property
    def genesis_transactions(self):
        return self.genesis_txns

    def create_client(self, port: int):
        return Client(name=randomString(6),
                      basedirpath=self.base_dir,
                      ha=('127.0.0.1', port))

    def steward_agent(self):
        return self._steward_agent

    # def setup_local_node(self, name, sigseed, override=True):
    #     _, verkey = initNodeKeysForBothStacks(name, self.base_dir, sigseed, override)

    def _generate_genesis_files(self):

        pool_txns, domain_txns = self._split_pool_and_domain()

        # TODO make Ledger a context manager
        pl = TestNetworkSetup.init_pool_ledger(appendToLedgers=False,
                                               baseDir=self.base_dir,
                                               config=self.config,
                                               envName='test')
        pl_lines = self._add_and_stop(pool_txns, pl)

        dl = TestNetworkSetup.init_domain_ledger(
            appendToLedgers=False,
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
        with open(ledger._transactionLog.db_path) as f:
            return f.readlines()
