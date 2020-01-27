import json
from collections import namedtuple
from typing import Iterable

import pytest
from indy.ledger import build_pool_config_request, build_nym_request

from plenum.common.messages.node_messages import PrePrepare, Prepare, Commit
from plenum.common.request import Request
from plenum.common.signer_simple import SimpleSigner
from plenum.common.util import compare_3PC_keys
from plenum.server.catchup.node_leecher_service import NodeLeecherService
from plenum.test.delayers import DEFAULT_DELAY, icDelay, cr_delay
from plenum.test.helper import max_3pc_batch_limits, sdk_get_replies, sdk_check_reply, \
    random_string, sdk_gen_pool_request, sdk_sign_and_submit_req_obj
from plenum.test.node_catchup.helper import ensure_all_nodes_have_same_data
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from plenum.test.stasher import start_delaying, stop_delaying_and_process, delay_rules
from plenum.test.test_node import ensureElectionsDone
from plenum.test.view_change_service.helper import trigger_view_change
from stp_core.loop.eventually import eventually


@pytest.fixture(scope="module")
def tconf(tconf):
    with max_3pc_batch_limits(tconf, size=1) as tconf:
        yield tconf


@pytest.fixture(scope='module')
def sdk_wallet_new_steward(looper, sdk_pool_handle, sdk_wallet_trustee):
    wh, client_did = sdk_add_new_nym(looper, sdk_pool_handle,
                                     sdk_wallet_trustee,
                                     alias='new_steward_qwerty',
                                     role='STEWARD')
    return wh, client_did


def test_view_change_during_alternating_unstash(looper, txnPoolNodeSet, sdk_pool_handle,
                                                sdk_wallet_trustee, sdk_wallet_new_steward, tconf):
    slow_node = txnPoolNodeSet[-1]
    other_nodes = txnPoolNodeSet[:-1]

    slow_stasher = slow_node.nodeIbStasher
    other_stashers = [n.nodeIbStasher for n in other_nodes]
    all_stashers = [n.nodeIbStasher for n in txnPoolNodeSet]

    # Ensure that pool has expected 3PC state
    for node in txnPoolNodeSet:
        assert node.master_replica.last_ordered_3pc == (0, 1)

    # Prevent ordering of some requests
    start_delaying(all_stashers, delay_3pc_after(0, 7, Prepare, Commit))

    # Stop ordering on slow node and send requests
    slow_node_after_5 = start_delaying(slow_stasher, delay_3pc_after(0, 5, Commit))
    slow_node_until_5 = start_delaying(slow_stasher, delay_3pc_after(0, 0))
    reqs_view_0 = sdk_send_alternating_ledgers_requests(looper, sdk_pool_handle,
                                                        sdk_wallet_trustee, sdk_wallet_new_steward, 8)

    # Make pool order first 2 batches and pause
    pool_after_3 = start_delaying(other_stashers, delay_3pc_after(0, 3))
    looper.run(eventually(check_nodes_ordered_till, other_nodes, 0, 3))

    # Start catchup, continue ordering everywhere (except two last batches on slow node)
    with delay_rules(slow_stasher, cr_delay()):
        slow_node._do_start_catchup(just_started=False)
        looper.run(eventually(check_catchup_is_started, slow_node))
        stop_delaying_and_process(pool_after_3)
        looper.run(eventually(check_nodes_ordered_till, other_nodes, 0, 7))

    # Finish catchup and continue processing on slow node
    looper.run(eventually(check_catchup_is_finished, slow_node))
    stop_delaying_and_process(slow_node_until_5)
    looper.run(eventually(check_nodes_ordered_till, [slow_node], 0, 5))

    # Start view change and allow slow node to get remaining commits
    with delay_rules(all_stashers, icDelay()):
        trigger_view_change(txnPoolNodeSet)
        looper.runFor(0.1)
    stop_delaying_and_process(slow_node_after_5)

    # Ensure that expected number of requests was ordered
    replies = sdk_get_replies(looper, reqs_view_0)
    for req in replies[:6]:
        sdk_check_reply(req)

    # Ensure that everything is ok
    ensureElectionsDone(looper, txnPoolNodeSet)
    ensure_all_nodes_have_same_data(looper, txnPoolNodeSet)


def sdk_gen_domain_request(looper, sdk_wallet):
    _, did = sdk_wallet
    target_did = SimpleSigner(seed=random_string(32).encode()).identifier
    req = looper.loop.run_until_complete(build_nym_request(did, target_did, None, None, None))
    return Request(**json.loads(req))


def sdk_gen_config_request(looper, sdk_wallet):
    _, did = sdk_wallet
    req = looper.loop.run_until_complete(build_pool_config_request(did, True, False))
    return Request(**json.loads(req))


def sdk_send_alternating_ledgers_requests(looper, pool_h, sdk_wallet_trustee, sdk_wallet_new_steward, count: int):
    node_alias = random_string(7)
    node_did = SimpleSigner(seed=random_string(32).encode()).identifier

    ReqFactory = namedtuple('ReqFactory', 'wallet create')
    req_factories = [
        ReqFactory(wallet=sdk_wallet_new_steward,
                   create=lambda: sdk_gen_pool_request(looper, sdk_wallet_new_steward, node_alias, node_did)),
        ReqFactory(wallet=sdk_wallet_trustee,
                   create=lambda: sdk_gen_domain_request(looper, sdk_wallet_trustee)),
        ReqFactory(wallet=sdk_wallet_trustee,
                   create=lambda: sdk_gen_config_request(looper, sdk_wallet_trustee))
    ]

    res = []
    for i in range(count):
        factory = req_factories[i % len(req_factories)]

        req = factory.create()
        res.append(sdk_sign_and_submit_req_obj(looper, pool_h, factory.wallet, req))
        looper.runFor(0.1)  # Give nodes some time to start ordering, so that requests are really alternating
    return res


def delay_3pc_after(view_no, pp_seq_no, *args):
    if not args:
        args = (PrePrepare, Prepare, Commit)

    def _delayer(msg_frm):
        msg, frm = msg_frm
        if not isinstance(msg, args):
            return
        if msg.viewNo != view_no:
            return
        if msg.ppSeqNo <= pp_seq_no:
            return
        return DEFAULT_DELAY

    _delayer.__name__ = "delay_3pc_after({}, {}, {})".format(view_no, pp_seq_no, args)
    return _delayer


def check_nodes_ordered_till(nodes: Iterable, view_no: int, pp_seq_no: int):
    for node in nodes:
        assert compare_3PC_keys((view_no, pp_seq_no), node.master_replica.last_ordered_3pc) >= 0


def check_catchup_is_started(node):
    assert node.ledgerManager._node_leecher._state != NodeLeecherService.State.Idle


def check_catchup_is_finished(node):
    assert node.ledgerManager._node_leecher._state == NodeLeecherService.State.Idle
