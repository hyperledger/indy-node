from plenum.common.constants import VERKEY
from plenum.common.signer_simple import SimpleSigner
from plenum.common.types import PrePrepare

from plenum.common.signer_did import DidSigner
from plenum.common.util import randomString
from plenum.test.helper import waitForSufficientRepliesForRequests
from plenum.test.test_node import getPrimaryReplica
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.test.helper import addRole
from sovrin_common.identity import Identity


def test_successive_batch_do_no_change_state(looper, tdirWithPoolTxns,
                                            tdirWithDomainTxnsUpdated,
                                            nodeSet, tconf,
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

    def specificPrePrepare(wrappedMsg):
        nonlocal pp_seq_no_to_delay
        msg, sender = wrappedMsg
        if isinstance(msg, PrePrepare) and \
                        msg.instId == 0 and \
                        msg.ppSeqNo == pp_seq_no_to_delay:
            return 5

    for node in other_nodes:
        node.nodeIbStasher.delay(specificPrePrepare)

    def new_identity():
        wallet = Wallet('some_name')
        signer = DidSigner()
        new_idr, _ = wallet.addIdentifier(signer=signer)
        verkey = wallet.getVerkey(new_idr)
        idy = Identity(identifier=new_idr,
                       verkey=verkey,
                       role=None)
        return idy

    idy = new_identity()
    new_idr = idy.identifier
    verkey = idy.verkey

    all_reqs = []

    def submit_id_req(idy):
        nonlocal all_reqs
        trusteeWallet.updateTrustAnchoredIdentity(idy)
        reqs = trusteeWallet.preparePending()
        all_reqs.extend(reqs)
        trustee.submitReqs(*reqs)

    # Setting the same verkey twice but in different batches with different
    #  request ids
    for i in range(2):
        submit_id_req(idy)
        looper.runFor(.2)

    waitForSufficientRepliesForRequests(looper, trustee, requests=all_reqs)

    for node in nodeSet:
        data = node.reqHandler.idrCache.getNym(new_idr, isCommitted=True)
        assert data[VERKEY] == verkey

    pp_seq_no_to_delay = 3
    for node in other_nodes:
        node.nodeIbStasher.delay(specificPrePrepare)

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

    waitForSufficientRepliesForRequests(looper, trustee, requests=all_reqs)

    for node in nodeSet:
        data = node.reqHandler.idrCache.getNym(new_idr, isCommitted=True)
        assert data[VERKEY] == verkey
