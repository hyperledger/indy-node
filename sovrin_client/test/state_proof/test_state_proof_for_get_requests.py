import pytest
from common.serializers.serialization import domain_state_serializer

from plenum.common.constants import TARGET_NYM, TXN_TYPE, RAW, DATA, \
    STATE_PROOF, ROOT_HASH, MULTI_SIGNATURE, PROOF_NODES, ROLE, VERKEY
from plenum.common.types import f

from sovrin_common.constants import GET_ATTR, GET_NYM
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
        print(reply)
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


def test_state_proof_returned_for_get_nym(looper,
                                          trustAnchor,
                                          trustAnchorWallet,
                                          userWalletA):
    """
    Tests that state proof is returned in the reply for GET_NYM transactions
    """
    client = trustAnchor
    dest = userWalletA.defaultId

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
        print(reply)
        result = reply['result']
        assert DATA in result
        assert result[DATA]
        data = domain_state_serializer.deserialize(result[DATA])
        assert ROLE in data
        assert VERKEY in data
        assert f.IDENTIFIER.nm in data
        state_proof = result[STATE_PROOF]
        assert ROOT_HASH in state_proof
        assert state_proof[ROOT_HASH]
        assert MULTI_SIGNATURE in state_proof
        assert state_proof[MULTI_SIGNATURE]
        assert state_proof[MULTI_SIGNATURE][0]
        assert state_proof[MULTI_SIGNATURE][1]
        assert PROOF_NODES in state_proof
        assert state_proof[PROOF_NODES]
