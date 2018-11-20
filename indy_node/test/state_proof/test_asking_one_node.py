import pytest

from indy_node.test.state_proof.helper import sdk_submit_operation_and_get_replies
from plenum.common.constants import TARGET_NYM, TXN_TYPE, RAW
from indy_common.constants import GET_ATTR

# fixtures
from indy_node.test.attrib_txn.test_nym_attrib import attributeData, \
    attributeName, attributeValue, sdk_added_raw_attribute

from plenum.test.delayers import req_delay
from plenum.test.stasher import delay_rules


@pytest.mark.skip('Broken State Proof validation due to different expected state keys in txn type field')
def test_client_gets_read_reply_from_1_node_only(looper,
                                                 nodeSet,
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

    # the order of nodes the client sends requests to is [Alpha, Beta, Gamma, Delta]
    # delay all requests to Beta, Gamma and Delta
    # we expect that it's sufficient for the client to get Reply from Alpha only
    stashers = [n.clientIbStasher for n in nodeSet[1:]]
    with delay_rules(stashers, req_delay()):
        sdk_submit_operation_and_get_replies(looper, sdk_pool_handle,
                                             sdk_wallet_trustee,
                                             get_attr_operation)
