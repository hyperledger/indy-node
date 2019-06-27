import json
import types

import pytest

from indy.did import create_and_store_my_did
from indy_node.persistence.idr_cache import IdrCache
from plenum.common.constants import VERKEY, DOMAIN_LEDGER_ID
from plenum.common.messages.node_messages import Commit
from plenum.common.util import randomString
from plenum.test.helper import sdk_get_and_check_replies
from indy_node.test.helper import sdk_rotate_verkey
from plenum.test.node_catchup.helper import waitNodeDataEquality
from plenum.test.delayers import icDelay
from plenum.test.pool_transactions.helper import sdk_add_new_nym, prepare_nym_request, \
    sdk_sign_and_send_prepared_request
from stp_core.common.log import getlogger
from stp_core.loop.eventually import eventually

logger = getlogger()


@pytest.fixture(scope="module")
def tconf(tconf, request):
    # Delaying performance checks since delaying 3PC messages in the test
    old_freq = tconf.PerfCheckFreq
    old_bt = tconf.Max3PCBatchWait
    old_bs = tconf.Max3PCBatchSize
    old_bf = tconf.Max3PCBatchesInFlight
    tconf.PerfCheckFreq = 50
    tconf.Max3PCBatchWait = .01
    tconf.Max3PCBatchSize = 1
    tconf.Max3PCBatchesInFlight = 5

    def reset():
        tconf.PerfCheckFreq = old_freq
        tconf.Max3PCBatchWait = old_bt
        tconf.Max3PCBatchSize = old_bs
        tconf.Max3PCBatchesInFlight = old_bf

    request.addfinalizer(reset)
    return tconf


@pytest.mark.skip(reason="get_req_handler is not supported yet")
def test_successive_batch_do_no_change_state(looper,
                                             tconf, nodeSet,
                                             sdk_pool_handle,
                                             sdk_wallet_trustee,
                                             monkeypatch):
    """
    Send 2 NYM txns in different batches such that the second batch does not
    change state so that state root remains same, but keep the identifier
    and reqId different. Make sure the first request is not ordered by the
    primary before PRE-PREPARE for the second is sent.
    Also check reject and commit
    :return:
    """

    # Disable view change during this test
    for n in nodeSet:
        n.nodeIbStasher.delay(icDelay())

    # Delay only first PRE-PREPARE
    delay_cm_duration = 10

    def delay_commits(wrappedMsg):
        msg, sender = wrappedMsg
        if isinstance(msg, Commit) and msg.instId == 0:
            return delay_cm_duration

    def check_verkey(i, vk):
        for node in nodeSet:
            data = node.idrCache.getNym(i, isCommitted=True)
            assert data[VERKEY] == vk

    def check_uncommitted(count):
        for node in nodeSet:
            assert len(node.idrCache.un_committed) == count

    for node in nodeSet:
        for rpl in node.replicas.values():
            monkeypatch.setattr(rpl, '_request_missing_three_phase_messages',
                                lambda *x, **y: None)

    wh, did = sdk_wallet_trustee
    seed = randomString(32)
    (new_did, verkey) = looper.loop.run_until_complete(
        create_and_store_my_did(wh, json.dumps({'seed': seed})))

    sdk_add_new_nym(looper, sdk_pool_handle,
                    sdk_wallet_trustee, dest=new_did,
                    verkey=verkey)

    for node in nodeSet:
        node.nodeIbStasher.delay(delay_commits)

    # Setting the same verkey thrice but in different batches with different
    # request ids
    for _ in range(3):
        verkey = sdk_rotate_verkey(looper, sdk_pool_handle,
                                   wh, new_did, new_did)
        logger.debug('{} rotates his key to {}'.
                     format(new_did, verkey))

    # Number of uncommitted entries is 0
    looper.run(eventually(check_uncommitted, 0))

    check_verkey(new_did, verkey)

    # Setting the verkey to `x`, then `y` and then back to `x` but in different
    # batches with different request ids. The idea is to change
    # state root to `t` then `t'` and then back to `t` and observe that no
    # errors are encountered

    seed = randomString(32)
    (new_client_did, verkey) = looper.loop.run_until_complete(
        create_and_store_my_did(wh, json.dumps({'seed': seed})))
    sdk_add_new_nym(looper, sdk_pool_handle,
                    sdk_wallet_trustee, dest=new_client_did,
                    verkey=verkey)

    x_seed = randomString(32)
    verkey = sdk_rotate_verkey(looper, sdk_pool_handle, wh,
                               new_client_did, new_client_did)
    logger.debug('{} rotates his key to {}'.
                 format(new_client_did, verkey))

    y_seed = randomString(32)
    sdk_rotate_verkey(looper, sdk_pool_handle, wh,
                      new_client_did, new_client_did)
    logger.debug('{} rotates his key to {}'.
                 format(new_client_did, verkey))

    verkey = sdk_rotate_verkey(looper, sdk_pool_handle, wh,
                      new_client_did, new_client_did)
    logger.debug('{} rotates his key to {}'.
                 format(new_client_did, verkey))

    # Number of uncommitted entries is 0
    looper.run(eventually(check_uncommitted, 0))

    check_verkey(new_client_did, verkey)
    monkeypatch.undo()

    # Delay COMMITs so that IdrCache can be checked for correct
    # number of entries

    uncommitteds = {}
    methods = {}
    for node in nodeSet:
        cache = node.idrCache  # type: IdrCache
        uncommitteds[cache._name] = []
        # Since the post batch creation handler is registered (added to a list),
        # find it and patch it
        dh = node.get_req_handler(DOMAIN_LEDGER_ID)
        for i, handler in enumerate(dh.post_batch_creation_handlers):
            # Find the cache's post create handler, not hardcoding names of
            # class or functions as they can change with refactoring.
            if handler.__func__.__qualname__ == '{}.{}'.format(cache.__class__.__name__,
                                                               cache.currentBatchCreated.__name__):
                cre = dh.post_batch_creation_handlers[i]
                break
        com = cache.onBatchCommitted
        methods[cache._name] = (cre, com)

        # Patch methods to record and check roots after commit

        def patched_cre(self, stateRoot, ppTime):
            uncommitteds[self._name].append(stateRoot)
            return methods[self._name][0](stateRoot, ppTime)

        def patched_com(self, stateRoot):
            assert uncommitteds[self._name][0] == stateRoot
            rv = methods[self._name][1](stateRoot)
            uncommitteds[self._name] = uncommitteds[self._name][1:]
            return rv

        dh.post_batch_creation_handlers[i] = types.MethodType(patched_cre, cache)
        cache.onBatchCommitted = types.MethodType(patched_com, cache)

    # Set verkey of multiple identities
    more = 5
    keys = {}
    reqs = []
    for _ in range(more):
        seed = randomString(32)
        nym_request, new_did = looper.loop.run_until_complete(
            prepare_nym_request(sdk_wallet_trustee, seed,
                                None, None))
        keys[new_did] = json.loads(nym_request)['operation']['verkey']
        reqs.append(
            sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                               sdk_pool_handle, nym_request))
        looper.runFor(tconf.Max3PCBatchWait + 0.1)

    # Correct number of uncommitted entries
    looper.run(eventually(check_uncommitted, more, retryWait=1))

    sdk_get_and_check_replies(looper, reqs)

    # Number of uncommitted entries is 0
    looper.run(eventually(check_uncommitted, 0))

    # The verkeys are correct
    for i, v in keys.items():
        check_verkey(i, v)

    waitNodeDataEquality(looper, nodeSet[0], *nodeSet[1:])

    for _ in range(3):
        seed = randomString(32)
        nym_request, new_did = looper.loop.run_until_complete(
            prepare_nym_request(sdk_wallet_trustee, seed,
                                None, None))
        reqs.append(
            sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                               sdk_pool_handle, nym_request))
        looper.runFor(tconf.Max3PCBatchWait + 0.1)

    # Correct number of uncommitted entries
    looper.run(eventually(check_uncommitted, 3, retryWait=1))

    # Check batch reject
    for node in nodeSet:
        cache = node.idrCache
        initial = cache.un_committed
        cache.batchRejected()
        # After reject, last entry is removed
        assert cache.un_committed == initial[:-1]
        root = cache.un_committed[0][0]
        cache.onBatchCommitted(root)
        # Calling commit with same root results in Assertion error
        with pytest.raises(AssertionError):
            cache.onBatchCommitted(root)
