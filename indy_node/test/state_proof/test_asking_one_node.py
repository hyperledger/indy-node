import pytest

from indy_node.test.state_proof.helper import sdk_submit_operation_and_get_result
from plenum.common.constants import TARGET_NYM, TXN_TYPE, RAW
from indy_common.constants import GET_ATTR

# fixtures
from indy_node.test.attrib_txn.test_nym_attrib import attributeData, \
    attributeName, attributeValue, sdk_added_raw_attribute


def test_client_gets_read_reply_from_1_node_only(looper,
                                                 nodeSetWithOneNodeResponding,
                                                 sdk_added_raw_attribute,
                                                 attributeName,
                                                 sdk_pool_handle,
                                                 sdk_wallet_trustee):
    """
    Tests that client could send get-requests to only one node instead of n
    """
    # Prepare and send get-request
    get_attr_operation = {
        TARGET_NYM: sdk_added_raw_attribute['result']['txn']['data']['dest'],
        TXN_TYPE: GET_ATTR,
        RAW: attributeName
    }

    sdk_submit_operation_and_get_result(looper, sdk_pool_handle,
                                        sdk_wallet_trustee,
                                        get_attr_operation)
