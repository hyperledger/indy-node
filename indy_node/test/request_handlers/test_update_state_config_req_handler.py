import functools
import os

import pytest
import time
import json

from common.serializers.serialization import domain_state_serializer
from indy_common.authorize.auth_actions import AuthActionAdd
from indy_common.authorize.auth_constraints import AuthConstraint, ConstraintsSerializer
from indy_common.state import config
from indy_node.server.node_bootstrap import NodeBootstrap
from ledger.compact_merkle_tree import CompactMerkleTree
from plenum.common.constants import TXN_TYPE, NYM, ROLE, TRUSTEE, STEWARD, CONFIG_LEDGER_ID, TXN_METADATA, \
    TXN_METADATA_SEQ_NO
from plenum.common.ledger import Ledger
from plenum.common.txn_util import reqToTxn, get_payload_data
from plenum.common.util import randomString
from plenum.server.database_manager import DatabaseManager
from plenum.server.replica import Replica
from plenum.common.request import Request
from plenum.server.request_managers.write_request_manager import WriteRequestManager
from plenum.test.testing_utils import FakeSomething
from state.pruning_state import PruningState
from storage.kv_in_memory import KeyValueStorageInMemory

from indy_node.test.helper import build_auth_rule_request_json


def reset_state(db_manager, lid):
    db_manager.databases[lid].state = PruningState(KeyValueStorageInMemory())
    db_manager._init_db_list()
    return db_manager


@pytest.fixture
def prepare_request(looper, sdk_wallet_trustee):
    constraint = AuthConstraint(TRUSTEE,
                                1)
    action = AuthActionAdd(txn_type=NYM,
                           field=ROLE,
                           value=STEWARD)
    auth_params = {
        "constraint": constraint.as_dict,
        "auth_action": "ADD",
        "auth_type": NYM,
        'field': ROLE,
        "new_value": STEWARD
    }
    req_json = build_auth_rule_request_json(
        looper, sdk_wallet_trustee[1], **auth_params
    )
    return action, constraint, Request(**json.loads(req_json))


def test_update_state(write_manager,
                      db_manager,
                      prepare_request,
                      constraint_serializer):
    action, constraint, request = prepare_request
    head_hash_before = db_manager.get_state(CONFIG_LEDGER_ID).headHash
    txn = reqToTxn(request)
    write_manager.update_state(txn, isCommitted=False)
    head_hash_after = db_manager.get_state(CONFIG_LEDGER_ID).headHash
    from_state = db_manager.get_state(CONFIG_LEDGER_ID).get(
        config.make_state_path_for_auth_rule(action.get_action_id()),
        isCommitted=False)
    assert constraint_serializer.deserialize(from_state) == constraint
    assert head_hash_after != head_hash_before


def test_uncommitted_state_after_apply(write_manager,
                                       db_manager,
                                       constraint_serializer,
                                       prepare_request):
    action, constraint, request = prepare_request

    write_manager.apply_request(request, int(time.time()))
    assert len(db_manager.get_ledger(CONFIG_LEDGER_ID).uncommittedTxns) == 1
    assert db_manager.get_state(CONFIG_LEDGER_ID).committedHeadHash != \
        db_manager.get_state(CONFIG_LEDGER_ID).headHash
    from_state = db_manager.get_state(CONFIG_LEDGER_ID).get(
        config.make_state_path_for_auth_rule(action.get_action_id()),
        isCommitted=False)
    assert constraint_serializer.deserialize(from_state) == constraint


def test_init_state_from_ledger(write_manager,
                                db_manager,
                                constraint_serializer,
                                prepare_request):
    reset_state(db_manager, CONFIG_LEDGER_ID)
    req_count = 1
    action, constraint, request = prepare_request
    txn = reqToTxn(request)
    txn[TXN_METADATA][TXN_METADATA_SEQ_NO] = 1
    """Add txn to ledger"""
    db_manager.get_ledger(CONFIG_LEDGER_ID).appendTxns([txn])
    db_manager.get_ledger(CONFIG_LEDGER_ID).commitTxns(req_count)
    # ToDo: ugly fix... Refactor this on pluggable req handler integration phase
    init_state_from_ledger = functools.partial(
        NodeBootstrap.init_state_from_ledger,
        FakeSomething(
            node=FakeSomething(update_txn_with_extra_data=lambda txn: txn,
                write_manager=write_manager)))
    """Check that txn is not exist in state"""
    assert db_manager.get_state(CONFIG_LEDGER_ID).get(config.make_state_path_for_auth_rule(action.get_action_id()),
                            isCommitted=False) is None
    assert db_manager.get_state(CONFIG_LEDGER_ID).get(config.make_state_path_for_auth_rule(action.get_action_id()),
                            isCommitted=True) is None
    txns_from_ledger = [t for t in db_manager.get_ledger(CONFIG_LEDGER_ID).getAllTxn()]
    """Check, that txn exist in ledger"""
    assert len(txns_from_ledger) == 1
    assert get_payload_data(txns_from_ledger[0][1]) == get_payload_data(txn)
    """Emulating node starting"""
    init_state_from_ledger(db_manager.get_state(CONFIG_LEDGER_ID),
                           db_manager.get_ledger(CONFIG_LEDGER_ID))
    """Check that txn was added into state"""
    from_state = db_manager.get_state(CONFIG_LEDGER_ID) .get(
        config.make_state_path_for_auth_rule(action.get_action_id()),
        isCommitted=True)
    assert constraint_serializer.deserialize(from_state) == constraint
