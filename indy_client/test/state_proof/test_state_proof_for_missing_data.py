from plenum.common.constants import TARGET_NYM, TXN_TYPE, RAW, DATA, NAME, VERSION, ORIGIN
from plenum.test.helper import waitForSufficientRepliesForRequests, getRepliesFromClientInbox

from indy_client.test.state_proof.helper import check_valid_proof
from indy_common.constants import GET_ATTR, GET_NYM, GET_SCHEMA, GET_CLAIM_DEF, REF, SIGNATURE_TYPE, \
    ATTR_NAMES


# fixtures, do not remove


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
        check_valid_proof(reply, client)


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
        check_valid_proof(reply, client)


def test_state_proof_returned_for_missing_schema(looper,
                                                 trustAnchor,
                                                 trustAnchorWallet):
    """
    Tests that state proof is returned in the reply for GET_NYM transactions
    """
    client = trustAnchor
    dest = trustAnchorWallet.defaultId
    schema_name = "test_schema"
    schema_version = "1.0"
    get_schema_operation = {
        TARGET_NYM: dest,
        TXN_TYPE: GET_SCHEMA,
        DATA: {
            NAME: schema_name,
            VERSION: schema_version,
        }
    }
    get_schema_request = trustAnchorWallet.signOp(get_schema_operation)
    trustAnchorWallet.pendRequest(get_schema_request)
    pending = trustAnchorWallet.preparePending()
    client.submitReqs(*pending)
    waitForSufficientRepliesForRequests(looper, trustAnchor, requests=pending)
    replies = getRepliesFromClientInbox(client.inBox, get_schema_request.reqId)
    for reply in replies:
        result = reply['result']
        assert ATTR_NAMES not in result[DATA]
        check_valid_proof(reply, client)


def test_state_proof_returned_for_missing_claim_def(looper,
                                                    trustAnchor,
                                                    trustAnchorWallet):
    """
    Tests that state proof is returned in the reply for GET_NYM transactions
    """
    client = trustAnchor
    dest = trustAnchorWallet.defaultId
    get_claim_def_operation = {
        ORIGIN: dest,
        TXN_TYPE: GET_CLAIM_DEF,
        REF: 12,
        SIGNATURE_TYPE: 'CL'
    }
    get_schema_request = trustAnchorWallet.signOp(get_claim_def_operation)
    trustAnchorWallet.pendRequest(get_schema_request)
    pending = trustAnchorWallet.preparePending()
    client.submitReqs(*pending)
    waitForSufficientRepliesForRequests(looper, trustAnchor, requests=pending)
    replies = getRepliesFromClientInbox(client.inBox, get_schema_request.reqId)
    for reply in replies:
        result = reply['result']
        assert DATA not in result or result[DATA] is None
        check_valid_proof(reply, client)
