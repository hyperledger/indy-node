from types import MethodType

import logging
import pytest

from indy_node.server.node import Node
from plenum.common.batched import Batched
from plenum.test.delayers import cDelay, lsDelay
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from plenum.test.test_node import getNonPrimaryReplicas
from stp_core.common.log import getlogger
from stp_core.loop.eventually import eventually

logger = getlogger()
whitelist = ["is not connected - message will not be sent immediately."]


@pytest.fixture(scope="module")
def tconf(tconf):
    oldMax3PCBatchSize = tconf.Max3PCBatchSize
    tconf.Max3PCBatchSize = 1

    yield tconf

    tconf.Max3PCBatchSize = oldMax3PCBatchSize


@pytest.fixture(scope="module")
def disable_transport_batching():
    original_should_batch = Batched._should_batch
    Batched._should_batch = lambda self, msgs: False

    yield

    Batched._should_batch = original_should_batch


# Enable blowing up for log messages with WARNING and higher severity levels
concerningLogLevels = [logging.WARNING,
                       logging.ERROR,
                       logging.CRITICAL]


def test_batch_rejected_on_catchup_start_can_be_ordered_before_ledgers_sync(
        looper,
        tdirWithPoolTxns,
        tdirWithDomainTxns,
        nodeSet,
        sdk_pool_handle,
        sdk_wallet_trust_anchor,
        allPluginsPath,
        tconf,
        disable_transport_batching):
    """
    Verifies that a batch rejected due to catch-up start can be successfully
    re-applied and ordered later before ledgers synchronization without any
    warnings.

    In the test we perform stashing / unstashing messages and patching /
    unpatching methods to ensure the desired order of events for the following
    scenario:

    1. Start a pool of 4 nodes. One node with a master replica not being
    a primary suffers from a slow network connection. We name this node slow.
    2. Start a client.
    3. Send a write request from the client to the pool.
    4. All the 3PC messages for this request are sent, received and handled by
    all the nodes except that COMMIT messages are not received by the slow node.
    5. The other nodes reach a consensus and order the batch.
    6. Initiate a catch-up of the slow node by calling its start_catchup method.
    7. The slow node rejects the unordered batch.
    8. The slow node sends MESSAGE_REQUEST for LEDGER_STATUS to the other nodes.
    9. The slow node receives the COMMIT messages from the other nodes.
    10. The slow node gets ORDER messages from its replicas and stashes them
    since it is not in participating mode.
    11. The slow node receives LEDGER_STATUS messages from the other nodes.
    12. Prior to ledgers synchronization the slow node processes the stashed
    ORDER messages. When it is processing the ORDER message from the master
    replica, it re-applies the batch and orders it.
    13. The slow node synchronizes its ledgers and completes the catch-up.
    """

    non_primary_replicas_of_master = getNonPrimaryReplicas(nodeSet, 0)
    slow_node = non_primary_replicas_of_master[0].node

    slow_node.nodeIbStasher.delay(cDelay(300))
    slow_node.start_catchup = MethodType(patched_start_catchup, slow_node)

    send_random_requests(looper, sdk_pool_handle, sdk_wallet_trust_anchor, 1)

    no_more_catchups_needed_call_times_before = \
        slow_node.spylog.count(Node.no_more_catchups_needed.__name__)
    on_batch_rejected_call_times_before = \
        slow_node.spylog.count(Node.onBatchRejected.__name__)
    on_batch_created_call_times_before = \
        slow_node.spylog.count(Node.onBatchCreated.__name__)
    process_ordered_call_times_before = \
        slow_node.spylog.count(Node.processOrdered.__name__)

    slow_node.start_catchup()

    def check_catchup_done():
        assert slow_node.spylog.count(Node.no_more_catchups_needed.__name__) > \
               no_more_catchups_needed_call_times_before

    looper.run(eventually(check_catchup_done, retryWait=1, timeout=10))

    on_batch_rejected_call_times_after = \
        slow_node.spylog.count(Node.onBatchRejected.__name__)
    on_batch_created_call_times_after = \
        slow_node.spylog.count(Node.onBatchCreated.__name__)
    process_ordered_call_times_after = \
        slow_node.spylog.count(Node.processOrdered.__name__)

    assert on_batch_rejected_call_times_after \
           - on_batch_rejected_call_times_before == 1

    assert on_batch_created_call_times_after \
           - on_batch_created_call_times_before == 1

    assert process_ordered_call_times_after \
           - process_ordered_call_times_before == 2  # one per replica
    last_2_process_ordered_results = \
        [call.result for call
         in slow_node.spylog.getAll(Node.processOrdered.__name__)[-2:]]
    assert True in last_2_process_ordered_results  # True for master replica


def patched_start_catchup(self, *args, **kwargs):
    Node.start_catchup(self, *args, **kwargs)

    self.nodeIbStasher.reset_delays_and_process_delayeds()
    self.nodeIbStasher.delay(lsDelay(300))

    self.try_processing_ordered = \
        MethodType(patched_try_processing_ordered, self)
    self.start_catchup = MethodType(Node.start_catchup, self)


def patched_try_processing_ordered(self, msg):
    Node.try_processing_ordered(self, msg)

    if msg.instId == 0:
        self.nodeIbStasher.reset_delays_and_process_delayeds()

        self.try_processing_ordered = \
            MethodType(Node.try_processing_ordered, self)


def send_random_requests(looper, sdk_pool_handle, sdk_wallet_trust_anchor, count: int):
    logger.info('{} random requests will be sent'.format(count))
    for i in range(count):
        sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trust_anchor)
