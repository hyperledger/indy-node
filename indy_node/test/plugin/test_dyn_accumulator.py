from copy import copy

import pytest

from indy_node.server.plugin.agent_authz.dynamic_accumulator import \
    DynamicAccumulator
from indy_node.server.plugin.agent_authz.helper import \
    update_accumulator_with_multiple_vals
from storage.test.conftest import parametrised_storage

G = 5
N = 104729


@pytest.fixture()
def dyn_accum(parametrised_storage) -> DynamicAccumulator:
    db = DynamicAccumulator(G, N, parametrised_storage)
    return db


def test_add_commitments(dyn_accum):
    assert dyn_accum.uncommitted_value == G
    assert dyn_accum.committed_value == G

    new_vals = [2, 3, 5, 7]
    for v in new_vals:
        dyn_accum.add_commitment(v)

    assert dyn_accum.uncommitted_value == update_accumulator_with_multiple_vals(G, new_vals, N)
    assert dyn_accum.committed_value == G
    assert not dyn_accum.has_committed_commitment(3)
    assert not dyn_accum.has_committed_commitment(4)

    dyn_accum.commit()
    assert dyn_accum.uncommitted_value == update_accumulator_with_multiple_vals(
        G, new_vals, N)
    assert dyn_accum.committed_value == dyn_accum.uncommitted_value
    assert dyn_accum.has_committed_commitment(3)
    assert not dyn_accum.has_committed_commitment(4)


def test_add_remove_commitments(dyn_accum):
    add_vals = [2, 3, 5, 7]
    for v in add_vals:
        dyn_accum.add_commitment(v)

    # Remove from uncommitted values
    rem_vals = [3, 5]
    for v in rem_vals:
        dyn_accum.remove_commitment(v)

    assert dyn_accum.uncommitted_value == update_accumulator_with_multiple_vals(
        G, set(add_vals).difference(set(rem_vals)), N)
    assert dyn_accum.committed_value == G

    dyn_accum.commit()
    assert dyn_accum.uncommitted_value == update_accumulator_with_multiple_vals(
        G, set(add_vals).difference(set(rem_vals)), N)
    assert dyn_accum.committed_value == dyn_accum.uncommitted_value


def test_add_remove_commitments_committed(dyn_accum):
    add_vals = [2, 3, 5, 7]
    for v in add_vals:
        dyn_accum.add_commitment(v)
    dyn_accum.commit()
    dyn_accum.new_batch_added()

    a1 = dyn_accum.committed_value

    for v in [11, 13]:
        dyn_accum.add_commitment(v)
        add_vals.append(v)

    # Remove from committed values
    rem_vals = [3, 5]
    for v in rem_vals:
        dyn_accum.remove_commitment(v)
    assert dyn_accum.uncommitted_value == update_accumulator_with_multiple_vals(
        G, set(add_vals).difference(set(rem_vals)), N)
    assert dyn_accum.committed_value == a1

    dyn_accum.commit()

    assert dyn_accum.uncommitted_value == update_accumulator_with_multiple_vals(
        G, set(add_vals).difference(set(rem_vals)), N)
    assert dyn_accum.committed_value == dyn_accum.uncommitted_value


@pytest.fixture(params=['commit', 'no_commit'])
def to_commit(request):
    if request.param == 'commit':
        return True
    if request.param == 'no_commit':
        return False


def test_add_remove_commitments_committed_and_uncommitted(to_commit, dyn_accum):
    add_vals = [2, 3, 5, 7]
    for v in add_vals:
        dyn_accum.add_commitment(v)
    dyn_accum.commit()
    dyn_accum.new_batch_added()

    for v in [11, 13]:
        dyn_accum.add_commitment(v)
        add_vals.append(v)
    if to_commit:
        dyn_accum.commit()
        dyn_accum.new_batch_added()

    for v in [17, 19]:
        dyn_accum.add_commitment(v)
        add_vals.append(v)

    if to_commit:
        dyn_accum.commit()
        dyn_accum.new_batch_added()

    a1 = dyn_accum.committed_value

    for v in [23, 29, 31]:
        dyn_accum.add_commitment(v)
        add_vals.append(v)

    # Remove from committed and uncommitted values
    rem_vals = [29, 17, 13, 3]
    for v in rem_vals:
        dyn_accum.remove_commitment(v)

    assert dyn_accum.uncommitted_value == update_accumulator_with_multiple_vals(
        G, set(add_vals).difference(set(rem_vals)), N)
    assert dyn_accum.committed_value == a1

    dyn_accum.commit()

    assert dyn_accum.uncommitted_value == update_accumulator_with_multiple_vals(
        G, set(add_vals).difference(set(rem_vals)), N)
    assert dyn_accum.committed_value == dyn_accum.uncommitted_value


def test_witness(dyn_accum):
    add_vals = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    for v in add_vals:
        dyn_accum.add_commitment(v)
    dyn_accum.commit()
    dyn_accum.new_batch_added()

    a1 = update_accumulator_with_multiple_vals(G, add_vals, N)
    assert dyn_accum.committed_value == a1
    assert dyn_accum.get_witness_data_for_committed_commitment(101) == (None, None, None)

    for i, n in enumerate(add_vals):
        assert dyn_accum.get_witness_data_for_committed_commitment(n) == (
        a1, update_accumulator_with_multiple_vals(G, add_vals[:i], N), add_vals[i+1:])

    for v in [37, 41, 43]:
        dyn_accum.add_commitment(v)
        add_vals.append(v)
    dyn_accum.commit()
    dyn_accum.new_batch_added()
    a2 = update_accumulator_with_multiple_vals(G, add_vals, N)

    for i, n in enumerate(add_vals):
        assert dyn_accum.get_witness_data_for_committed_commitment(n) == (
        a2, update_accumulator_with_multiple_vals(G, add_vals[:i], N), add_vals[i+1:])

    rem_vals = [29, 17, 13, 3]
    for v in rem_vals:
        dyn_accum.remove_commitment(v)

    # Only commit() should affect witness computation
    for i, n in enumerate(add_vals):
        assert dyn_accum.get_witness_data_for_committed_commitment(n) == (
        a2, update_accumulator_with_multiple_vals(G, add_vals[:i], N), add_vals[i+1:])

    dyn_accum.commit()
    dyn_accum.new_batch_added()
    a3 = update_accumulator_with_multiple_vals(G, set(add_vals).difference(set(rem_vals)), N)

    for i in rem_vals:
        assert dyn_accum.get_witness_data_for_committed_commitment(i) == (None, None, None)

    # For each element currently present in the accumulator
    for i in set(add_vals).difference(set(rem_vals)):
        final = copy(add_vals)
        for r in rem_vals:
            final.remove(r)
        idx = final.index(i)
        assert dyn_accum.get_witness_data_for_committed_commitment(i) == (
            a3, update_accumulator_with_multiple_vals(G, final[:idx], N),
            final[idx + 1:])