from plenum.common.constants import TARGET_NYM, TXN_TYPE, RAW, DATA
from plenum.test.helper import waitForSufficientRepliesForRequests, getRepliesFromClientInbox
from sovrin_common.constants import GET_ATTR, GET_NYM
from sovrin_client.test.state_proof.helper import check_valid_proof

# fixtures, do not remove
from sovrin_client.test.test_nym_attrib import attributeName


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
    for reply in replies:
        result = reply['result']
        assert DATA not in result or result[DATA] is None
        check_valid_proof(reply)


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
    for reply in replies:
        result = reply['result']
        assert DATA not in result or result[DATA] is None
        check_valid_proof(reply)
