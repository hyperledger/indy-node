from indy_client.test.state_proof.helper import sdk_submit_operation_and_get_replies
from plenum.common.constants import TARGET_NYM, TXN_TYPE, RAW
from indy_common.constants import GET_ATTR
from indy_client.test.test_nym_attrib import attributeData, \
    attributeName, attributeValue, sdk_added_raw_attribute


# for node in txnPoolNodeSet[1:]: node.clientstack.stop()

def test_state_proof_returned_for_get_attr(looper,
                                           sdk_added_raw_attribute,
                                           attributeName,
                                           sdk_pool_handle,
                                           sdk_wallet_trustee):
    """
    Tests that client could send get-requests to only one node instead of n
    """
    # Prepare and send get-request
    get_attr_operation = {
        TARGET_NYM: sdk_added_raw_attribute['operation']['dest'],
        TXN_TYPE: GET_ATTR,
        RAW: attributeName
    }
    # Get reply and verify that the only one received
    replies = sdk_submit_operation_and_get_replies(looper, sdk_pool_handle,
                                                   sdk_wallet_trustee,
                                                   get_attr_operation)

    assert len(replies) == 1
