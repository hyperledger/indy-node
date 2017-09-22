from hashlib import sha256
from common.serializers.serialization import domain_state_serializer


MARKER_ATTR = "\01"
MARKER_SCHEMA = "\02"
MARKER_CLAIM_DEF = "\03"
LAST_SEQ_NO = "lsn"
VALUE = "val"
LAST_UPDATE_TIME = "lut"


def make_state_path_for_nym(did) -> bytes:
    from plenum.server.domain_req_handler import DomainRequestHandler
    return DomainRequestHandler.nym_to_state_key(did)
    # return sha256(did.encode()).digest()


def make_state_path_for_attr(did, attr_name) -> bytes:
    nameHash = sha256(attr_name.encode()).hexdigest()
    return "{DID}:{MARKER}:{ATTR_NAME}"\
        .format(DID=did,
                MARKER=MARKER_ATTR,
                ATTR_NAME=nameHash).encode()


def make_state_path_for_schema(authors_did, schema_name, schema_version) -> bytes:
    return "{DID}:{MARKER}:{SCHEMA_NAME}:{SCHEMA_VERSION}" \
        .format(DID=authors_did,
                MARKER=MARKER_SCHEMA,
                SCHEMA_NAME=schema_name,
                SCHEMA_VERSION=schema_version).encode()


def make_state_path_for_claim_def(authors_did, schema_seq_no, signature_type) -> bytes:
    return "{DID}:{MARKER}:{SIGNATURE_TYPE}:{SCHEMA_SEQ_NO}" \
        .format(DID=authors_did,
                MARKER=MARKER_CLAIM_DEF,
                SIGNATURE_TYPE=signature_type,
                SCHEMA_SEQ_NO=schema_seq_no).encode()


def make_state_value(value, seqNo, txnTime):
    return domain_state_serializer.serialize({
        LAST_SEQ_NO: seqNo,
        LAST_UPDATE_TIME: txnTime,
        VALUE: value
    })

