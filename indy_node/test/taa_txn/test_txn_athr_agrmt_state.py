from _sha256 import sha256

import pytest

from indy_node.server.config_req_handler import ConfigReqHandler
from indy_node.test.taa_txn.helper import gen_txn_athr_agrmt
from ledger.compact_merkle_tree import CompactMerkleTree
from plenum.common.ledger import Ledger
from plenum.common.txn_util import reqToTxn
from plenum.test.testing_utils import FakeSomething
from state.pruning_state import PruningState
from storage.kv_in_memory import KeyValueStorageInMemory


@pytest.fixture
def config_state():
    return PruningState(KeyValueStorageInMemory())


@pytest.fixture
def config_ledger(tmpdir_factory):
    tdir = tmpdir_factory.mktemp('').strpath
    return Ledger(CompactMerkleTree(),
                  dataDir=tdir)


@pytest.fixture
def config_req_handler(config_state,
                       config_ledger):

    return ConfigReqHandler(config_ledger,
                            config_state,
                            idrCache=FakeSomething(),
                            upgrader=FakeSomething(),
                            poolManager=FakeSomething(),
                            poolCfg=FakeSomething(),
                            write_req_validator=FakeSomething())


def test_txn_athr_agrmt_updates_state(config_req_handler, sdk_wallet_trustee):
    version = 'some_version'
    text = 'some text'
    req = gen_txn_athr_agrmt(sdk_wallet_trustee[1], version=version, text=text)
    txn = reqToTxn(req)

    state = config_req_handler.state
    state_hash_before = state.headHash
    config_req_handler.updateState([txn])

    txn_hash = sha256('{}{}'.format(version, text).encode()).digest()

    assert state.headHash != state_hash_before
    assert state.get(':taa:latest'.encode()) == txn_hash
