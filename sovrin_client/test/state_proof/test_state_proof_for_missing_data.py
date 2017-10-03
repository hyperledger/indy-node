from common.serializers.serialization import domain_state_serializer
from plenum.common.constants import TARGET_NYM, TXN_TYPE, RAW, DATA, STATE_PROOF, ROOT_HASH, MULTI_SIGNATURE, \
    PROOF_NODES, NYM, ROLE, VERKEY, TXN_TIME
from plenum.common.types import f
from plenum.test.helper import waitForSufficientRepliesForRequests, getRepliesFromClientInbox
from sovrin_common.serialization import attrib_raw_data_serializer

from sovrin_common.constants import GET_ATTR, GET_NYM

# fixtures, do not remove
from sovrin_client.test.test_nym_attrib import attributeName


def check_valid_proof(replies):
    for reply in replies:
        result = reply['result']
        assert DATA not in result or result[DATA] is None
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


def test_state_proof_returned_for_missing_attr(looper,
                                               attributeName,
                                               trustAnchor,
                                               trustAnchorWallet):
    """
    Tests that state proof is returned in the reply for GET_ATTR transactions
    """
    client = trustAnchor
    get_attr_operation = {
        TARGET_NYM: trustAnchorWallet.defaultId,
        TXN_TYPE: GET_ATTR,
        RAW: attributeName
    }
    get_attr_request = trustAnchorWallet.signOp(get_attr_operation)
    trustAnchorWallet.pendRequest(get_attr_request)
    pending = trustAnchorWallet.preparePending()
    client.submitReqs(*pending)
    waitForSufficientRepliesForRequests(looper, trustAnchor, requests=pending)
    replies = getRepliesFromClientInbox(client.inBox, get_attr_request.reqId)
    check_valid_proof(replies)


def test_state_proof_returned_for_missing_nym(looper,
                                              trustAnchor,
                                              trustAnchorWallet,
                                              userWalletA):
    """
    Tests that state proof is returned in the reply for GET_NYM transactions
    """
    client = trustAnchor
    # Make not existing id
    dest = userWalletA.defaultId
    dest = dest[:-3]
    dest += "fff"

    get_nym_operation = {
        TARGET_NYM: dest,
        TXN_TYPE: GET_NYM
    }

    get_nym_request = trustAnchorWallet.signOp(get_nym_operation)
    trustAnchorWallet.pendRequest(get_nym_request)
    pending = trustAnchorWallet.preparePending()
    client.submitReqs(*pending)
    waitForSufficientRepliesForRequests(looper, trustAnchor, requests=pending)
    replies = getRepliesFromClientInbox(client.inBox, get_nym_request.reqId)
    check_valid_proof(replies)
