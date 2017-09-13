import pytest

from plenum.common.constants import TARGET_NYM, TXN_TYPE, RAW, DATA, \
    STATE_PROOF, ROOT_HASH, MULTI_SIGNATURE, PROOF_NODES
from sovrin_common.constants import GET_ATTR
from plenum.test.helper import waitForSufficientRepliesForRequests, \
    getRepliesFromClientInbox

# Fixtures, do not remove
from sovrin_node.test.helper import addAttributeAndCheck
from sovrin_client.client.wallet.attribute import Attribute, LedgerStore
from sovrin_client.test.test_nym_attrib import \
    addedRawAttribute, attributeName, attributeValue, attributeData



def test_state_proof_returned_for_get_attr(looper,
                                           addedRawAttribute,
                                           attributeName,
                                           attributeData,
                                           trustAnchor,
                                           trustAnchorWallet):
    """
    Tests that state proof is returned in the reply for GET_ATTR transactions
    """
    client = trustAnchor
    get_attr_operation = {
        TARGET_NYM: addedRawAttribute.dest,
        TXN_TYPE: GET_ATTR,
        RAW: attributeName
    }
    get_attr_request = trustAnchorWallet.signOp(get_attr_operation)
    trustAnchorWallet.pendRequest(get_attr_request)
    pending = trustAnchorWallet.preparePending()
    client.submitReqs(*pending)
    waitForSufficientRepliesForRequests(looper, trustAnchor, requests=pending)
    replies = getRepliesFromClientInbox(client.inBox, get_attr_request.reqId)
    expected_data = attributeData
    for reply in replies:
        result = reply['result']
        assert DATA in result
        assert result[DATA] == expected_data
        assert STATE_PROOF in result
        state_proof = result[STATE_PROOF]
        assert ROOT_HASH in state_proof
        assert state_proof[ROOT_HASH]
        assert MULTI_SIGNATURE in state_proof
        assert state_proof[MULTI_SIGNATURE]
        assert state_proof[MULTI_SIGNATURE][0]
        assert state_proof[MULTI_SIGNATURE][1]
        assert PROOF_NODES in state_proof
        assert state_proof[PROOF_NODES]
