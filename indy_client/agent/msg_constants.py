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

ACCEPT_INVITE = 'ACCEPT_INVITE'
INVITE_ACCEPTED = "INVITE_ACCEPTED"

# Claims message types
CLAIM_OFFER = 'CLAIM_OFFER'
CLAIM_REQUEST = 'CLAIM_REQUEST'
CLAIM = 'CLAIM'
AVAIL_CLAIM_LIST = 'AVAIL_CLAIM_LIST'
REQ_AVAIL_CLAIMS = 'REQ_AVAIL_CLAIMS'

# TODO Why do we have this and AVAIL_CLAIM_LIST
NEW_AVAILABLE_CLAIMS = "NEW_AVAILABLE_CLAIMS"

# Proofs message types
PROOF_REQUEST = 'PROOF_REQUEST'
PROOF = 'PROOF'
PROOF_STATUS = 'PROOF_STATUS'


ISSUER_DID = 'issuer_did'
CLAIM_REQ_FIELD = 'blinded_ms'
CLAIM_FIELD = 'claim'
PROOF_FIELD = 'proof'
SCHEMA_SEQ_NO = 'schema_seq_no'
PROOF_REQUEST_FIELD = 'proof_request'

# Proof request schema keys
PROOF_REQ_SCHEMA_NAME = 'name'
PROOF_REQ_SCHEMA_VERSION = 'version'
PROOF_REQ_SCHEMA_ATTRIBUTES = 'attributes'
PROOF_REQ_SCHEMA_VERIFIABLE_ATTRIBUTES = 'verifiableAttributes'

# Other
CLAIM_NAME_FIELD = "claimName"
REF_REQUEST_ID = "refRequestId"
REVOC_REG_SEQ_NO = "revoc_reg_seq_no"

# Error constants
ERR_NO_PROOF_REQUEST_SCHEMA_FOUND = 'Error: No proof request schema found'

"""
ACCEPT_INVITE
{
    "type": 'ACCEPT_INVITE',
    "identifier": <id>,
    "nonce": <nonce>,
    "signature" : <sig>
}


AVAIL_CLAIM_LIST
{
    'type': 'AVAIL_CLAIM_LIST',
    'claims_list': [
        "Name": "Transcript",
        "Version": "1.2",
        "Definition": {
            "Attributes": {
                "student_name": "string",
                "ssn": "int",
                "degree": "string",
                "year": "string",
                "status": "string"
            }
        }
    ],
    "signature" : <sig>
}

AVAIL_CLAIM_LIST
{
    'type': 'AVAIL_CLAIM_LIST',
    'claims_list': [
        "Name": "Transcript",
        "Version": "1.2",
        "Definition": {
            "Attributes": {
                "student_name": "string",
                "ssn": "int",
                "degree": "string",
                "year": "string",
                "status": "string"
            }
        }
    ],
    "signature" : <sig>
}

"""
