from plenum.common.constants import STATE_PROOF, ROOT_HASH, MULTI_SIGNATURE, \
    PROOF_NODES
from plenum.test.helper import getRepliesFromClientInbox, \
    waitForSufficientRepliesForRequests


def submit_operation_and_get_replies(looper, wallet, client, operation):
    request = wallet.signOp(operation)
    wallet.pendRequest(request)
    pending = wallet.preparePending()
    client.submitReqs(*pending)
    waitForSufficientRepliesForRequests(looper, client, requests=pending)
    return getRepliesFromClientInbox(client.inBox, request.reqId)


def check_valid_proof(reply, client):
    result = reply['result']
    assert STATE_PROOF in result
    state_proof = result[STATE_PROOF]
    assert ROOT_HASH in state_proof
    assert state_proof[ROOT_HASH]
    assert MULTI_SIGNATURE in state_proof
    assert state_proof[MULTI_SIGNATURE]
    assert state_proof[MULTI_SIGNATURE]["participants"]
    assert state_proof[MULTI_SIGNATURE]["pool_state_root"]
    assert state_proof[MULTI_SIGNATURE]["signature"]
    assert PROOF_NODES in state_proof
    assert state_proof[PROOF_NODES]
    assert client.take_one_proved({"mock-sender": reply}, "mock-request-id")
