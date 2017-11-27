import types

import pytest

from plenum.common.constants import VERKEY
from plenum.common.signer_simple import SimpleSigner
from plenum.common.messages.node_messages import PrePrepare, Commit
from plenum.common.signer_did import DidSigner
from plenum.common.util import randomString
from plenum.test.delayers import cDelay
from plenum.test.helper import waitForSufficientRepliesForRequests
from plenum.test.node_catchup.helper import waitNodeDataEquality
from plenum.test.test_node import getPrimaryReplica
from indy_client.client.wallet.wallet import Wallet
from indy_common.identity import Identity
from stp_core.loop.eventually import eventually


@pytest.fixture(scope="module")
def tconf(tconf, request):
    # Delaying performance checks since delaying 3PC messages in the test
    old_freq = tconf.PerfCheckFreq
    tconf.PerfCheckFreq = 40

    def reset():
        tconf.PerfCheckFreq = old_freq

    request.addfinalizer(reset)
    return tconf


def test_successive_batch_do_no_change_state(looper, tdirWithPoolTxns,
                                             tdirWithDomainTxnsUpdated,
                                             tconf, nodeSet,
                                             trustee, trusteeWallet, monkeypatch):
    """
    Send 2 NYM txns in different batches such that the second batch does not
    change state so that state root remains same, but keep the identifier
    and reqId different. Make sure the first request is not ordered by the
    primary before PRE-PREPARE for the second is sent.
    Also check reject and commit
    :return:
    """
    prim_node = getPrimaryReplica(nodeSet, 0).node
    other_nodes = [n for n in nodeSet if n != prim_node]
    all_reqs = []

    # Delay only first PRE-PREPARE
    pp_seq_no_to_delay = 1
    delay_pp_duration = 5
    delay_cm_duration = 10

    def specific_pre_prepare(wrappedMsg):
        nonlocal pp_seq_no_to_delay
        msg, sender = wrappedMsg
        if isinstance(msg, PrePrepare) and \
                msg.instId == 0 and \
                msg.ppSeqNo == pp_seq_no_to_delay:
            return delay_pp_duration

    def delay_commits(wrappedMsg):
        msg, sender = wrappedMsg
        if isinstance(msg, Commit) and msg.instId == 0:
            return 10

    def new_identity():
        wallet = Wallet(randomString(5))
        signer = DidSigner()
        new_idr, _ = wallet.addIdentifier(signer=signer)
        verkey = wallet.getVerkey(new_idr)
        idy = Identity(identifier=new_idr,
                       verkey=verkey,
                       role=None)
        return idy, wallet

    def submit_id_req(idy, wallet=None, client=None):
        nonlocal all_reqs
        wallet = wallet if wallet is not None else trusteeWallet
        client = client if client is not None else trustee
        wallet.updateTrustAnchoredIdentity(idy)
        reqs = wallet.preparePending()
        all_reqs.extend(reqs)
        client.submitReqs(*reqs)

    def submit_id_req_and_wait(idy, wallet=None, client=None):
        submit_id_req(idy, wallet=wallet, client=client)
        looper.runFor(.2)

    def check_verkey(i, vk):
        for node in nodeSet:
            data = node.idrCache.getNym(i, isCommitted=True)
            assert data[VERKEY] == vk

    def check_uncommitted(count):
        for node in nodeSet:
            assert len(node.idrCache.un_committed) == count

    # for node in other_nodes:
    #     node.nodeIbStasher.delay(specific_pre_prepare)
    for node in nodeSet:
        node.nodeIbStasher.delay(delay_commits)
        for rpl in node.replicas:
            monkeypatch.setattr(rpl, '_request_missing_three_phase_messages',
                                lambda *x, **y: None)

    idy, new_wallet = new_identity()
    new_idr = idy.identifier
    verkey = idy.verkey

    # Setting the same verkey thrice but in different batches with different
    #  request ids
    submit_id_req(idy)
    waitForSufficientRepliesForRequests(looper, trustee, requests=all_reqs[-1:],
                                        add_delay_to_timeout=delay_cm_duration)
    for _ in range(3):
        submit_id_req_and_wait(idy, new_wallet)
        # submit_id_req(idy)
        # looper.runFor(.2)

    waitForSufficientRepliesForRequests(looper, trustee, requests=all_reqs,
                                        add_delay_to_timeout=delay_cm_duration)

    # Number of uncommitted entries is 0
    looper.run(eventually(check_uncommitted, 0))

    check_verkey(new_idr, verkey)

    pp_seq_no_to_delay = 4
    # for node in other_nodes:
    #     node.nodeIbStasher.delay(specific_pre_prepare)
    #     # disable requesting missing 3 phase messages. Otherwise PP delay won't work
    #     for rpl in node.replicas:
    #         monkeypatch.setattr(rpl, '_request_missing_three_phase_messages',
    #                             lambda *x, **y: None)
    for node in nodeSet:
        node.nodeIbStasher.delay(delay_commits)
        for rpl in node.replicas:
            monkeypatch.setattr(rpl, '_request_missing_three_phase_messages',
                                lambda *x, **y: None)

    # Setting the verkey to `x`, then `y` and then back to `x` but in different
    # batches with different request ids. The idea is to change
    # state root to `t` then `t'` and then back to `t` and observe that no
    # errors are encountered

    idy, new_wallet = new_identity()
    new_idr = idy.identifier
    verkey = idy.verkey
    submit_id_req_and_wait(idy)
    # submit_id_req(idy)
    # looper.runFor(.2)

    # new_verkey = SimpleSigner().verkey
    # idy.verkey = new_verkey
    # submit_id_req(idy)
    # looper.runFor(.2)
    old_signer = new_wallet.idsToSigners[idy.identifier]
    new_signer = SimpleSigner(identifier=idy.identifier)
    new_wallet.updateSigner(idy.identifier, new_signer)
    idy.verkey = new_wallet.getVerkey(idy.identifier)
    submit_id_req_and_wait(idy, new_wallet)

    # idy.verkey = verkey
    # submit_id_req(idy)
    # looper.runFor(.2)
    new_wallet.updateSigner(idy.identifier, old_signer)
    idy.verkey = new_wallet.getVerkey(idy.identifier)
    submit_id_req_and_wait(idy, new_wallet)

    waitForSufficientRepliesForRequests(looper, trustee, requests=all_reqs,
                                        add_delay_to_timeout=delay_cm_duration)

    # Number of uncommitted entries is 0
    looper.run(eventually(check_uncommitted, 0))

    check_verkey(new_idr, verkey)
    monkeypatch.undo()

    # Delay COMMITs so that IdrCache can be checked for correct
    # number of entries

    uncommitteds = {}
    methods = {}
    for node in nodeSet:
        node.nodeIbStasher.delay(delay_commits)

        cache = node.idrCache
        uncommitteds[cache._name] = []

        cre = cache.currentBatchCreated
        com = cache.onBatchCommitted
        methods[cache._name] = (cre, com)

        # Patch methods to record and check roots after commit

        def patched_cre(self, stateRoot):
            uncommitteds[self._name].append(stateRoot)
            return methods[self._name][0](stateRoot)

        def patched_com(self, stateRoot):
            assert uncommitteds[self._name][0] == stateRoot
            rv = methods[self._name][1](stateRoot)
            uncommitteds[self._name] = uncommitteds[self._name][1:]
            return rv

        cache.currentBatchCreated = types.MethodType(patched_cre, cache)
        cache.onBatchCommitted = types.MethodType(patched_com, cache)

    # Set verkey of multiple identities
    more = 5
    keys = {}
    for _ in range(more):
        idy, _ = new_identity()
        keys[idy.identifier] = idy.verkey
        submit_id_req(idy)
        looper.runFor(.01)

    # Correct number of uncommitted entries
    looper.run(eventually(check_uncommitted, more, retryWait=1))

    waitForSufficientRepliesForRequests(looper, trustee, requests=all_reqs,
                                        add_delay_to_timeout=delay_cm_duration)

    # Number of uncommitted entries is 0
    looper.run(eventually(check_uncommitted, 0))

    # The verkeys are correct
    for i, v in keys.items():
        check_verkey(i, v)

    waitNodeDataEquality(looper, nodeSet[0], *nodeSet[1:])

    keys = {}
    for _ in range(3):
        idy, _ = new_identity()
        keys[idy.identifier] = idy.verkey
        submit_id_req(idy)
        looper.runFor(.01)

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
