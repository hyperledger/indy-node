import pytest
import time
from indy_common.constants import REVOC_REG_DEF_ID, ISSUED, REVOKED, \
    PREV_ACCUM, ACCUM, TXN_TYPE, CRED_DEF_ID, VALUE, TAG
from indy_common.types import Request
from indy_common.state import domain
from plenum.common.types import f
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.util import randomString


def test_validation_with_prev_accum_but_empty_ledger(
        build_txn_for_revoc_def_entry_by_default,
        create_node_and_not_start):
    node = create_node_and_not_start
    req_entry = build_txn_for_revoc_def_entry_by_default
    del req_entry['operation'][VALUE][ISSUED]
    del req_entry['operation'][VALUE][REVOKED]
    with pytest.raises(InvalidClientRequest, match="but there is no previous"):
        node.write_manager.dynamic_validation(Request(**req_entry), 0)


def test_validation_with_right_accums_but_empty_indices(
        build_txn_for_revoc_def_entry_by_default,
        create_node_and_not_start):
    node = create_node_and_not_start
    req_entry = build_txn_for_revoc_def_entry_by_default
    node.write_manager.apply_request(Request(**req_entry), int(time.time()))
    req_entry['operation'][VALUE][PREV_ACCUM] = req_entry['operation'][VALUE][ACCUM]
    req_entry['operation'][VALUE][ACCUM] = randomString(10)
    del req_entry['operation'][VALUE][ISSUED]
    del req_entry['operation'][VALUE][REVOKED]
    with pytest.raises(InvalidClientRequest, match="lists are empty"):
        node.write_manager.dynamic_validation(Request(**req_entry), 0)


def test_validation_with_unexpected_accum(
        build_txn_for_revoc_def_entry_by_default,
        create_node_and_not_start):
    node = create_node_and_not_start
    req_entry = build_txn_for_revoc_def_entry_by_default
    node.write_manager.apply_request(Request(**req_entry), int(time.time()))
    with pytest.raises(InvalidClientRequest, match="must be equal to the last accumulator value"):
        node.write_manager.dynamic_validation(Request(**req_entry), 0)


def test_validation_with_same_revoked_by_default(
        build_txn_for_revoc_def_entry_by_default,
        create_node_and_not_start):
    node = create_node_and_not_start
    req_entry = build_txn_for_revoc_def_entry_by_default
    req_entry['operation'][VALUE][REVOKED] = [1, 2]
    node.write_manager.apply_request(Request(**req_entry), int(time.time()))
    req_entry['operation'][VALUE][PREV_ACCUM] = req_entry['operation'][VALUE][ACCUM]
    req_entry['operation'][VALUE][ACCUM] = randomString(10)
    with pytest.raises(InvalidClientRequest, match="are already revoked in current state"):
        node.write_manager.dynamic_validation(Request(**req_entry), 0)


def test_validation_with_issued_no_revoked_before_by_default(
        build_txn_for_revoc_def_entry_by_default,
        create_node_and_not_start):
    node = create_node_and_not_start
    req_entry = build_txn_for_revoc_def_entry_by_default
    req_entry['operation'][VALUE][REVOKED] = [1, 2]
    node.write_manager.apply_request(Request(**req_entry), int(time.time()))
    req_entry['operation'][VALUE][ISSUED] = [3, 4]
    req_entry['operation'][VALUE][REVOKED] = []
    req_entry['operation'][VALUE][PREV_ACCUM] = req_entry['operation'][VALUE][ACCUM]
    req_entry['operation'][VALUE][ACCUM] = randomString(10)
    with pytest.raises(InvalidClientRequest, match="are not present in the current revoked list"):
        node.write_manager.dynamic_validation(Request(**req_entry), 0)


def test_validation_with_same_issued_by_demand(
        build_txn_for_revoc_def_entry_by_demand,
        create_node_and_not_start):
    node = create_node_and_not_start
    req_entry = build_txn_for_revoc_def_entry_by_demand
    req_entry['operation'][VALUE][ISSUED] = [1, 2]
    node.write_manager.apply_request(Request(**req_entry), int(time.time()))
    req_entry['operation'][VALUE][PREV_ACCUM] = req_entry['operation'][VALUE][ACCUM]
    req_entry['operation'][VALUE][ACCUM] = randomString(10)
    req_entry['operation'][VALUE][ISSUED] = [1, 2]
    with pytest.raises(InvalidClientRequest, match="are already issued in current state"):
        node.write_manager.dynamic_validation(Request(**req_entry), 0)


def test_validation_with_revoked_no_issued_before_by_demand(
        build_txn_for_revoc_def_entry_by_demand,
        create_node_and_not_start):
    node = create_node_and_not_start
    req_entry = build_txn_for_revoc_def_entry_by_demand
    req_entry['operation'][VALUE][ISSUED] = [1, 2]
    node.write_manager.apply_request(Request(**req_entry), int(time.time()))
    req_entry['operation'][VALUE][REVOKED] = [3, 4]
    req_entry['operation'][VALUE][PREV_ACCUM] = req_entry['operation'][VALUE][ACCUM]
    req_entry['operation'][VALUE][ACCUM] = randomString(10)
    with pytest.raises(InvalidClientRequest, match="are not present in the current issued list"):
        node.write_manager.dynamic_validation(Request(**req_entry), 0)


def test_validation_if_issued_revoked_has_same_index(
        build_txn_for_revoc_def_entry_by_default,
        create_node_and_not_start):
    node = create_node_and_not_start
    req_entry = build_txn_for_revoc_def_entry_by_default
    req_entry['operation'][VALUE][REVOKED] = [1, 2]
    req_entry['operation'][VALUE][ISSUED] = [1, 2]
    with pytest.raises(InvalidClientRequest, match="Can not have an index in both 'issued' and 'revoked' lists"):
        node.write_manager.dynamic_validation(Request(**req_entry), 0)


def test_validation_if_revoc_def_does_not_exist(
        build_txn_for_revoc_def_entry_by_default,
        create_node_and_not_start):
    path = ":".join([f.IDENTIFIER.nm,
                     domain.MARKER_REVOC_DEF,
                     CRED_DEF_ID,
                     TXN_TYPE,
                     TAG])
    node = create_node_and_not_start
    req_entry = build_txn_for_revoc_def_entry_by_default
    req_entry['operation'][REVOC_REG_DEF_ID] = path
    with pytest.raises(InvalidClientRequest, match="There is no any REVOC_REG_DEF"):
        node.write_manager.dynamic_validation(Request(**req_entry), 0)


def test_validation_with_equal_accums_but_not_empty_indices(
        build_txn_for_revoc_def_entry_by_default,
        create_node_and_not_start):
    node = create_node_and_not_start
    req_entry = build_txn_for_revoc_def_entry_by_default
    node.write_manager.apply_request(Request(**req_entry), int(time.time()))
    req_entry['operation'][VALUE][PREV_ACCUM] = req_entry['operation'][VALUE][ACCUM]
    req_entry['operation'][VALUE][REVOKED] = [100, 200]
    with pytest.raises(InvalidClientRequest, match="Got equal accum and prev_accum"):
        node.write_manager.dynamic_validation(Request(**req_entry), 0)
