from types import MethodType

import logging
import pytest

from indy_client.client.client import Client
from indy_client.client.wallet.wallet import Wallet
from indy_common.identity import Identity
from indy_node.server.node import Node
from indy_client.test.conftest import nodeSet
from plenum.common.batched import Batched
from plenum.test.delayers import cDelay, lsDelay
from plenum.test.helper import waitForSufficientRepliesForRequests
from plenum.test.test_node import getNonPrimaryReplicas
from stp_core.common.log import getlogger
from stp_core.loop.eventually import eventually

logger = getlogger()


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


concerningLogLevels = [logging.WARNING,
                       logging.ERROR,
                       logging.CRITICAL]


def test_3pc_batch_reverted_on_catchup_start_can_be_ordered_before_ledgers_sync(
        looper,
        tdirWithPoolTxns,
        tdirWithDomainTxns,
        nodeSet,
        trustAnchor,
        trustAnchorWallet,
        allPluginsPath,
        tconf,
        disable_transport_batching):

    non_primary_replicas_of_master = getNonPrimaryReplicas(nodeSet, 0)
    slow_node = non_primary_replicas_of_master[0].node

    slow_node.nodeIbStasher.delay(cDelay(300))
    slow_node.start_catchup = MethodType(patched_start_catchup, slow_node)

    requests = send_random_requests(trustAnchorWallet, trustAnchor, 1)
    waitForSufficientRepliesForRequests(looper, trustAnchor, requests=requests)

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


def patched_start_catchup(self):
    Node.start_catchup(self)

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


def send_random_requests(wallet: Wallet, client: Client, count: int):
    logger.info('{} random requests will be sent'.format(count))
    for i in range(count):
        idr, signer = wallet.addIdentifier()
        idy = Identity(identifier=idr, verkey=signer.verkey)
        wallet.addTrustAnchoredIdentity(idy)
    requests = wallet.preparePending()
    return client.submitReqs(*requests)[0]
