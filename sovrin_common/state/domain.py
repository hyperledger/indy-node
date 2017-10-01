import json
from hashlib import sha256
from common.serializers.serialization import domain_state_serializer
from plenum.common.constants import RAW, ENC, HASH, TXN_TIME, TXN_TYPE, TARGET_NYM, DATA, NAME, VERSION
from plenum.common.types import f
from sovrin_common.serialization import attrib_raw_data_serializer
from sovrin_common.constants import ATTRIB, GET_ATTR, REF, SIGNATURE_TYPE

MARKER_ATTR = "\01"
MARKER_SCHEMA = "\02"
MARKER_CLAIM_DEF = "\03"
LAST_SEQ_NO = "lsn"
VALUE = "val"
LAST_UPDATE_TIME = "lut"


def make_state_path_for_nym(did) -> bytes:
    # TODO: This is duplicated in plenum.DimainRequestHandler
    return sha256(did.encode()).digest()


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


def prepare_nym_for_state(txn):
    # TODO: this is semi-duplicated in plenum.DomainRequestHandler
    data = txn.get(DATA)
    nym = txn[TARGET_NYM]
    value = domain_state_serializer.serialize(data)
    key = make_state_path_for_nym(nym)
    return key, value


def prepare_attr_for_state(txn):
    """
    Make key(path)-value pair for state from ATTRIB or GET_ATTR
    :return: state path, state value, value for attribute store
    """
    assert txn[TXN_TYPE] in {ATTRIB, GET_ATTR}
    nym = txn.get(TARGET_NYM)
    attr_key, value = parse_attr_txn(txn)
    hashed_value = hash_of(value) if value else ''
    seq_no = txn[f.SEQ_NO.nm]
    txn_time = txn[TXN_TIME]
    value_bytes = encode_state_value(hashed_value, seq_no, txn_time)
    path = make_state_path_for_attr(nym, attr_key)
    return path, value, hashed_value, value_bytes


def prepare_claim_def_for_state(txn):
    origin = txn.get(f.IDENTIFIER.nm)
    schema_seq_no = txn.get(REF)
    if schema_seq_no is None:
        raise ValueError("'{}' field is absent, "
                         "but it must contain schema seq no".format(REF))
    data = txn.get(DATA)
    if data is None:
        raise ValueError("'{}' field is absent, "
                         "but it must contain components of keys"
                         .format(DATA))
    signature_type = txn.get(SIGNATURE_TYPE, 'CL')
    path = make_state_path_for_claim_def(origin, schema_seq_no, signature_type)
    seq_no = txn[f.SEQ_NO.nm]
    txn_time = txn[TXN_TIME]
    value_bytes = encode_state_value(data, seq_no, txn_time)
    return path, value_bytes


def prepare_schema_for_state(txn):
    origin = txn.get(f.IDENTIFIER.nm)
    data = txn.get(DATA)
    schema_name = data[NAME]
    schema_version = data[VERSION]
    path = make_state_path_for_schema(origin, schema_name, schema_version)
    seq_no = txn[f.SEQ_NO.nm]
    txn_time = txn[TXN_TIME]
    value_bytes = encode_state_value(data, seq_no, txn_time)
    return path, value_bytes


def encode_state_value(value, seqNo, txnTime):
    return domain_state_serializer.serialize({
        LAST_SEQ_NO: seqNo,
        LAST_UPDATE_TIME: txnTime,
        VALUE: value
    })


def decode_state_value(ecnoded_value):
    decoded = domain_state_serializer.deserialize(ecnoded_value)
    value = decoded.get(VALUE)
    last_seq_no = decoded.get(LAST_SEQ_NO)
    last_update_time = decoded.get(LAST_UPDATE_TIME)
    return value, last_seq_no, last_update_time


def hash_of(text) -> str:
    if not isinstance(text, (str, bytes)):
        text = domain_state_serializer.serialize(text)
    if not isinstance(text, bytes):
        text = text.encode()
    return sha256(text).hexdigest()


def parse_attr_txn(txn):
    raw = txn.get(RAW)
    if raw:
        data = attrib_raw_data_serializer.deserialize(raw)
        # To exclude user-side formatting issues
        re_raw = attrib_raw_data_serializer.serialize(data,
                                                      toBytes=False)
        key, _ = data.popitem()
        return key, re_raw
    enc = txn.get(ENC)
    if enc:
        return hash_of(enc), enc
    hsh = txn.get(HASH)
    if hsh:
        return hsh, None
    raise ValueError("One of 'raw', 'enc', 'hash' "
                     "fields of ATTR must present")