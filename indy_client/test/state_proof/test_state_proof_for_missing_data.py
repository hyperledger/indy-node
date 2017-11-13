#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

from plenum.common.types import f

from plenum.common.constants import TARGET_NYM, TXN_TYPE, RAW, DATA, NAME, \
    VERSION, ORIGIN
from plenum.test.helper import waitForSufficientRepliesForRequests, \
    getRepliesFromClientInbox

from indy_client.test.state_proof.helper import check_valid_proof, \
    submit_operation_and_get_replies
from indy_common.constants import GET_ATTR, GET_NYM, GET_SCHEMA, GET_CLAIM_DEF,\
    REF, SIGNATURE_TYPE, ATTR_NAMES


# fixtures, do not remove
from indy_client.test.test_nym_attrib import \
    addedRawAttribute, attributeName, attributeValue, attributeData


def check_no_data_and_valid_proof(client, replies):
    for reply in replies:
        result = reply[f.RESULT.nm]
        assert result.get(DATA) is None
        check_valid_proof(reply, client)


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
    replies = submit_operation_and_get_replies(looper, trustAnchorWallet,
                                               trustAnchor, get_attr_operation)
    check_no_data_and_valid_proof(client, replies)


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

    replies = submit_operation_and_get_replies(looper, trustAnchorWallet,
                                               trustAnchor, get_nym_operation)
    check_no_data_and_valid_proof(client, replies)


def test_state_proof_returned_for_missing_schema(looper,
                                                 trustAnchor,
                                                 trustAnchorWallet):
    """
    Tests that state proof is returned in the reply for GET_SCHEMA transactions
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
    replies = submit_operation_and_get_replies(looper, trustAnchorWallet,
                                               trustAnchor, get_schema_operation)
    for reply in replies:
        result = reply[f.RESULT.nm]
        assert ATTR_NAMES not in result[DATA]
        check_valid_proof(reply, client)


def test_state_proof_returned_for_missing_claim_def(looper,
                                                    trustAnchor,
                                                    trustAnchorWallet):
    """
    Tests that state proof is returned in the reply for GET_CLAIM_DEF transactions
    """
    client = trustAnchor
    dest = trustAnchorWallet.defaultId
    get_claim_def_operation = {
        ORIGIN: dest,
        TXN_TYPE: GET_CLAIM_DEF,
        REF: 12,
        SIGNATURE_TYPE: 'CL'
    }
    replies = submit_operation_and_get_replies(looper, trustAnchorWallet,
                                               trustAnchor, get_claim_def_operation)
    check_no_data_and_valid_proof(client, replies)
