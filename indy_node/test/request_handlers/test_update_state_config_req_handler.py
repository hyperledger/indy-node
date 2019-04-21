import functools
import pytest
import time

from common.serializers.serialization import domain_state_serializer
from indy_common.authorize.auth_actions import AuthActionAdd
from indy_common.authorize.auth_constraints import AuthConstraint, ConstraintsSerializer
from indy_common.constants import AUTH_RULE
from indy_common.state import config
from indy_node.server.config_req_handler import ConfigReqHandler
from indy_node.server.node import Node
from ledger.compact_merkle_tree import CompactMerkleTree
from ledger.test.helper import create_default_ledger
from plenum.common.constants import TXN_TYPE, NYM, ROLE, TRUSTEE, STEWARD, CONFIG_LEDGER_ID, TXN_METADATA, \
    TXN_METADATA_SEQ_NO
from plenum.common.ledger import Ledger
from plenum.common.txn_util import reqToTxn, get_payload_data
from plenum.server.replica import Replica
from plenum.test.helper import sdk_gen_request
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
def constraint_serializer():
    return ConstraintsSerializer(domain_state_serializer)


@pytest.fixture
def fake_replica(config_ledger,
                 config_state):
    replica = FakeSomething(
        node=FakeSomething(getLedger=lambda *args, **kwargs: config_ledger,
                           getState=lambda *args, **kwargs: config_state,
                           onBatchRejected=lambda *args, **kwargs: True),
        logger=FakeSomething(info=lambda *args, **kwargs: True)
    )
    replica.revert = functools.partial(Replica.revert, replica)
    return replica


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


@pytest.fixture
def prepare_request(sdk_wallet_trustee):
    constraint = AuthConstraint(TRUSTEE,
                                1)
    action = AuthActionAdd(txn_type=NYM,
                           field=ROLE,
                           value=STEWARD)
    op = {TXN_TYPE: AUTH_RULE,
          "constraint": constraint.as_dict,
          "auth_action": "ADD",
          "auth_type": NYM,
          'field': ROLE,
          "new_value": STEWARD
          }
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    return action, constraint, req_obj


def test_update_state(config_req_handler,
                      prepare_request,
                      constraint_serializer):
    action, constraint, request = prepare_request
    head_hash_before = config_req_handler.state.headHash
    txn = reqToTxn(request)
    config_req_handler.updateState([txn], isCommitted=False)
    head_hash_after = config_req_handler.state.headHash
    from_state = config_req_handler.state.get(
        config.make_state_path_for_auth_rule(action.get_action_id()),
        isCommitted=False)
    assert constraint_serializer.deserialize(from_state) == constraint
    assert head_hash_after != head_hash_before


def test_uncommitted_state_after_apply(config_req_handler,
                                       constraint_serializer,
                                       prepare_request):
    action, constraint, request = prepare_request

    config_req_handler.apply(request, int(time.time()))
    assert len(config_req_handler.ledger.uncommittedTxns) == 1
    assert config_req_handler.state.committedHeadHash != \
        config_req_handler.state.headHash
    from_state = config_req_handler.state.get(
        config.make_state_path_for_auth_rule(action.get_action_id()),
        isCommitted=False)
    assert constraint_serializer.deserialize(from_state) == constraint


def test_revert_uncommitted_state(config_req_handler,
                                  constraint_serializer,
                                  prepare_request,
                                  fake_replica):
    action, constraint, request = prepare_request
    req_count = 1

    state_root_hash_before = config_req_handler.state.headHash

    config_req_handler.apply(request, int(time.time()))
    """
    Check, that request exist in uncommitted state
    """
    from_state = config_req_handler.state.get(
        config.make_state_path_for_auth_rule(action.get_action_id()),
        isCommitted=False)
    assert constraint_serializer.deserialize(from_state) == constraint

    fake_replica.revert(CONFIG_LEDGER_ID,
                        state_root_hash_before,
                        req_count)
    """
    Txn is reverted from ledger and state
    """
    assert len(config_req_handler.ledger.uncommittedTxns) == 0
    from_state = config_req_handler.state.get(
        config.make_state_path_for_auth_rule(action.get_action_id()),
        isCommitted=False)
    assert from_state is None


def test_init_state_from_ledger(config_ledger,
                                config_state,
                                config_req_handler,
                                constraint_serializer,
                                prepare_request):
    req_count = 1
    action, constraint, request = prepare_request
    txn = reqToTxn(request)
    txn[TXN_METADATA][TXN_METADATA_SEQ_NO] = 1
    """Add txn to ledger"""
    config_ledger.appendTxns([txn])
    config_ledger.commitTxns(req_count)
    init_state_from_ledger = functools.partial(Node.init_state_from_ledger,
                                               FakeSomething(update_txn_with_extra_data=lambda txn: txn))
    """Check that txn is not exist in state"""
    assert config_state.get(config.make_state_path_for_auth_rule(action.get_action_id()),
                            isCommitted=False) is None
    assert config_state.get(config.make_state_path_for_auth_rule(action.get_action_id()),
                            isCommitted=True) is None
    txns_from_ledger = [t for t in config_ledger.getAllTxn()]
    """Check, that txn exist in ledger"""
    assert len(txns_from_ledger) == 1
    assert get_payload_data(txns_from_ledger[0][1]) == get_payload_data(txn)
    """Emulating node starting"""
    init_state_from_ledger(config_state,
                           config_ledger,
                           config_req_handler)
    """Check that txn was added into state"""
    from_state = config_state.get(
        config.make_state_path_for_auth_rule(action.get_action_id()),
        isCommitted=True)
    assert constraint_serializer.deserialize(from_state) == constraint
