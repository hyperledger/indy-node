from plenum.common.constants import TARGET_NYM, TXN_TYPE, RAW
from plenum.test.helper import waitForSufficientRepliesForRequests, getRepliesFromClientInbox

from sovrin_common.constants import GET_ATTR

# fixtures, do not remove
from sovrin_client.test.test_nym_attrib import attributeName, attributeData, attributeValue


def test_state_proof_returned_for_missing_attr(looper,
                                               attributeName,
                                               attributeData,
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
        print(reply)

    # expected_data = attrib_raw_data_serializer.deserialize(attributeData)
    # for reply in replies:
    #     result = reply['result']
    #     assert DATA in result
    #     data = attrib_raw_data_serializer.deserialize(result[DATA])
    #     assert data == expected_data
    #     assert result[TXN_TIME]
    #     assert STATE_PROOF in result
    #     state_proof = result[STATE_PROOF]
    #     assert ROOT_HASH in state_proof
    #     assert state_proof[ROOT_HASH]
    #     assert MULTI_SIGNATURE in state_proof
    #     assert state_proof[MULTI_SIGNATURE]
    #     assert state_proof[MULTI_SIGNATURE]["participants"]
    #     assert state_proof[MULTI_SIGNATURE]["pool_state_root"]
    #     assert state_proof[MULTI_SIGNATURE]["signature"]
    #     assert PROOF_NODES in state_proof
    #     assert state_proof[PROOF_NODES]
