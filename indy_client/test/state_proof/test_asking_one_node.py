import pytest

from indy_client.test.state_proof.helper import submit_operation_and_get_replies
from plenum.common.constants import TARGET_NYM, TXN_TYPE, RAW
from indy_common.constants import GET_ATTR
from indy_client.test.test_nym_attrib import \
    addedRawAttribute, attributeName, attributeValue, attributeData


def make_client_send_requests_to_only_one_node(client):
    """
    Modifies client so that it sends requests only to one node
    """
    old_send = client.send

    def send(msg, *rids, signer = None):
        nodestack = client.nodestack
        the_one_remote = list(nodestack.remotes.keys())[0] if not rids else rids[0]
        return old_send(msg, the_one_remote, signer=signer)

    client.send = send
    return client


def test_state_proof_returned_for_get_attr(looper,
                                           addedRawAttribute,
                                           attributeName,
                                           trustAnchor,
                                           trustAnchorWallet):
    """
    Tests that client could send get-requests to only one node instead of n
    """
    client = trustAnchor
    client = make_client_send_requests_to_only_one_node(client)

    # Prepare and send get-request
    get_attr_operation = {
        TARGET_NYM: addedRawAttribute.dest,
        TXN_TYPE: GET_ATTR,
        RAW: attributeName
    }
    # Get reply and verify that the only one received
    replies = submit_operation_and_get_replies(looper, trustAnchorWallet,
                                               client,
                                               get_attr_operation)

    assert len(replies) == 1
