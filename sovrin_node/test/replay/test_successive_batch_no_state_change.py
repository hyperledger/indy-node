import pytest

from plenum.common.constants import VERKEY
from plenum.common.signer_simple import SimpleSigner
from plenum.common.types import PrePrepare, Commit
from plenum.common.signer_did import DidSigner
from plenum.test.delayers import cDelay
from plenum.test.helper import waitForSufficientRepliesForRequests
from plenum.test.test_node import getPrimaryReplica
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_common.identity import Identity
from stp_core.loop.eventually import eventually


@pytest.fixture(scope="module")
def tconf(tconf, request):
    old_freq = tconf.PerfCheckFreq
    tconf.PerfCheckFreq = 30

    def reset():
        tconf.PerfCheckFreq = old_freq

    request.addfinalizer(reset)
    return tconf


def test_successive_batch_do_no_change_state(looper, tdirWithPoolTxns,
                                            tdirWithDomainTxnsUpdated,
                                             tconf, nodeSet,
                                            trustee, trusteeWallet):
    """
    Send 2 NYM txns in different batches such that the second batch does not
    change state so that state root remains same, but keep the identifier
    and reqId different. Make sure the first request is not ordered by the
    primary before PRE-PREPARE for the second is sent.
    :return:
    """
    prim_node = getPrimaryReplica(nodeSet, 0).node
    other_nodes = [n for n in nodeSet if n != prim_node]
    # Delay only first PRE-PREPARE
    pp_seq_no_to_delay = 1

    def specific_pre_prepare(wrappedMsg):
        nonlocal pp_seq_no_to_delay
        msg, sender = wrappedMsg
        if isinstance(msg, PrePrepare) and \
                        msg.instId == 0 and \
                        msg.ppSeqNo == pp_seq_no_to_delay:
            return 5

    def new_identity():
        wallet = Wallet('some_name')
        signer = DidSigner()
        new_idr, _ = wallet.addIdentifier(signer=signer)
        verkey = wallet.getVerkey(new_idr)
        idy = Identity(identifier=new_idr,
                       verkey=verkey,
                       role=None)
        return idy

    def submit_id_req(idy):
        nonlocal all_reqs
        trusteeWallet.updateTrustAnchoredIdentity(idy)
        reqs = trusteeWallet.preparePending()
        all_reqs.extend(reqs)
        trustee.submitReqs(*reqs)

    def check_verkey(i, vk):
        for node in nodeSet:
            data = node.reqHandler.idrCache.getNym(i, isCommitted=True)
            assert data[VERKEY] == vk

    for node in other_nodes:
        node.nodeIbStasher.delay(specific_pre_prepare)

    idy = new_identity()
    new_idr = idy.identifier
    verkey = idy.verkey

    all_reqs = []

    # Setting the same verkey twice but in different batches with different
    #  request ids
    for _ in range(3):
        submit_id_req(idy)
        looper.runFor(.2)

    waitForSufficientRepliesForRequests(looper, trustee, requests=all_reqs,
                                        add_delay_to_timeout=5)
    check_verkey(new_idr, verkey)

    pp_seq_no_to_delay = 4
    for node in other_nodes:
        node.nodeIbStasher.delay(specific_pre_prepare)

    # Setting the verkey to `x`, then `y` and then back to `x` but in different
    # batches with different with different request ids. The idea is to change
    # state root to `t` then `t'` and then back to `t` and observe that no
    # errors are encountered

    idy = new_identity()
    new_idr = idy.identifier
    verkey = idy.verkey
    submit_id_req(idy)
    looper.runFor(.2)

    new_verkey = SimpleSigner().verkey
    idy.verkey = new_verkey
    submit_id_req(idy)
    looper.runFor(.2)

    idy.verkey = verkey
    submit_id_req(idy)
    looper.runFor(.2)

    waitForSufficientRepliesForRequests(looper, trustee, requests=all_reqs,
                                        add_delay_to_timeout=5)
    check_verkey(new_idr, verkey)

    # Dleay COMMITs so that IdrCache can be checked for correct
    # number of entries
    for node in nodeSet:
        def delay_commits(wrappedMsg):
            msg, sender = wrappedMsg
            if isinstance(msg, Commit) and msg.instId == 0:
                return 10
        node.nodeIbStasher.delay(delay_commits)

    # Set verkey of multiple identities
    more = 5
    keys = {}
    for _ in range(more):
        idy = new_identity()
        keys[idy.identifier] = idy.verkey
        submit_id_req(idy)
        looper.runFor(.01)

    def check_uncommitted(count):
        for node in nodeSet:
            assert len(node.reqHandler.idrCache.unCommitted) == count

    # Correct number of uncommitted entries
    looper.run(eventually(check_uncommitted, more))

    waitForSufficientRepliesForRequests(looper, trustee, requests=all_reqs,
                                        add_delay_to_timeout=10)

    # The verkeys are correct
    for i, v in keys.items():
        check_verkey(i, v)
