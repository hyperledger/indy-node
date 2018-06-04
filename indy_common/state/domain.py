from copy import deepcopy
from hashlib import sha256

from common.serializers.serialization import domain_state_serializer
from indy_common.constants import ATTRIB, GET_ATTR, REF, SIGNATURE_TYPE, REVOC_TYPE, TAG, CRED_DEF_ID, REVOC_REG_DEF_ID
from indy_common.serialization import attrib_raw_data_serializer
from plenum.common.constants import RAW, ENC, HASH, TXN_TIME, \
    TARGET_NYM, DATA, NAME, VERSION, ORIGIN, TYPE
from plenum.common.txn_util import get_type, get_payload_data, get_seq_no, get_txn_time, get_from
from plenum.common.types import f

MARKER_ATTR = "\01"
MARKER_SCHEMA = "\02"
MARKER_CLAIM_DEF = "\03"
# TODO: change previous markers in "request refactoring" sprint
MARKER_REVOC_DEF = "4"
MARKER_REVOC_REG_ENTRY = "5"
MARKER_REVOC_REG_ENTRY_ACCUM = "6"
LAST_SEQ_NO = "lsn"
VALUE = "val"
LAST_UPDATE_TIME = "lut"

ALL_ATR_KEYS = [RAW, ENC, HASH]


def make_state_path_for_nym(did) -> bytes:
    # TODO: This is duplicated in plenum.DimainRequestHandler
    return sha256(did.encode()).digest()


def make_state_path_for_attr(did, attr_name, attr_is_hash=False) -> bytes:
    nameHash = sha256(attr_name.encode()).hexdigest() if not attr_is_hash else attr_name
    return "{DID}:{MARKER}:{ATTR_NAME}" \
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


def make_state_path_for_revoc_def(authors_did, cred_def_id, revoc_def_type, revoc_def_tag) -> bytes:
    return "{DID}:{MARKER}:{CRED_DEF_ID}:{REVOC_DEF_TYPE}:{REVOC_DEF_TAG}" \
        .format(DID=authors_did,
                MARKER=MARKER_REVOC_DEF,
                CRED_DEF_ID=cred_def_id,
                REVOC_DEF_TYPE=revoc_def_type,
                REVOC_DEF_TAG=revoc_def_tag).encode()


def make_state_path_for_revoc_reg_entry(revoc_reg_def_id) -> bytes:
    return "{MARKER}:{REVOC_REG_DEF_ID}" \
        .format(MARKER=MARKER_REVOC_REG_ENTRY,
                REVOC_REG_DEF_ID=revoc_reg_def_id).encode()


def make_state_path_for_revoc_reg_entry_accum(revoc_reg_def_id) -> bytes:
    return "{MARKER}:{REVOC_REG_DEF_ID}" \
        .format(MARKER=MARKER_REVOC_REG_ENTRY_ACCUM,
                REVOC_REG_DEF_ID=revoc_reg_def_id).encode()


def prepare_get_nym_for_state(reply):
    data = reply.get(DATA)
    value = None
    if data is not None:
        parsed = domain_state_serializer.deserialize(data)
        parsed.pop(TARGET_NYM, None)
        value = domain_state_serializer.serialize(parsed)
    nym = reply[TARGET_NYM]
    key = make_state_path_for_nym(nym)
    return key, value


def prepare_attr_for_state(txn):
    """
    Make key(path)-value pair for state from ATTRIB or GET_ATTR
    :return: state path, state value, value for attribute store
    """
    assert get_type(txn) == ATTRIB
    txn_data = get_payload_data(txn)
    nym = txn_data[TARGET_NYM]
    attr_type, attr_key, value = parse_attr_txn(txn_data)
    hashed_value = hash_of(value) if value else ''
    seq_no = get_seq_no(txn)
    txn_time = get_txn_time(txn)
    value_bytes = encode_state_value(hashed_value, seq_no, txn_time)
    path = make_state_path_for_attr(nym, attr_key, attr_type == HASH)
    return attr_type, path, value, hashed_value, value_bytes


def prepare_claim_def_for_state(txn):
    txn_data = get_payload_data(txn)
    origin = get_from(txn)
    schema_seq_no = txn_data.get(REF)
    if schema_seq_no is None:
        raise ValueError("'{}' field is absent, "
                         "but it must contain schema seq no".format(REF))
    data = txn_data.get(DATA)
    if data is None:
        raise ValueError("'{}' field is absent, "
                         "but it must contain components of keys"
                         .format(DATA))
    signature_type = txn_data.get(SIGNATURE_TYPE, 'CL')
    path = make_state_path_for_claim_def(origin, schema_seq_no, signature_type)
    seq_no = get_seq_no(txn)
    txn_time = get_txn_time(txn)
    value_bytes = encode_state_value(data, seq_no, txn_time)
    return path, value_bytes


def prepare_revoc_def_for_state(txn):
    author_did = get_from(txn)
    txn_data = get_payload_data(txn)
    cred_def_id = txn_data.get(CRED_DEF_ID)
    revoc_def_type = txn_data.get(REVOC_TYPE)
    revoc_def_tag = txn_data.get(TAG)
    assert author_did
    assert cred_def_id
    assert revoc_def_type
    assert revoc_def_tag
    path = make_state_path_for_revoc_def(author_did,
                                         cred_def_id,
                                         revoc_def_type,
                                         revoc_def_tag)
    seq_no = get_seq_no(txn)
    txn_time = get_txn_time(txn)
    assert seq_no
    assert txn_time
    value_bytes = encode_state_value(txn_data, seq_no, txn_time)
    return path, value_bytes


def prepare_revoc_reg_entry_for_state(txn):
    author_did = get_from(txn)
    txn_data = get_payload_data(txn)
    revoc_reg_def_id = txn_data.get(REVOC_REG_DEF_ID)
    assert author_did
    assert revoc_reg_def_id
    path = make_state_path_for_revoc_reg_entry(revoc_reg_def_id=revoc_reg_def_id)

    seq_no = get_seq_no(txn)
    txn_time = get_txn_time(txn)
    assert seq_no
    assert txn_time
    # TODO: do not duplicate seqNo here
    # doing this now just for backward-compatibility
    txn_data = deepcopy(txn_data)
    txn_data[f.SEQ_NO.nm] = seq_no
    txn_data[TXN_TIME] = txn_time
    value_bytes = encode_state_value(txn_data, seq_no, txn_time)
    return path, value_bytes


def prepare_revoc_reg_entry_accum_for_state(txn):
    author_did = get_from(txn)
    txn_data = get_payload_data(txn)
    revoc_reg_def_id = txn_data.get(REVOC_REG_DEF_ID)
    seq_no = get_seq_no(txn)
    txn_time = get_txn_time(txn)
    assert author_did
    assert revoc_reg_def_id
    assert seq_no
    assert txn_time
    path = make_state_path_for_revoc_reg_entry_accum(revoc_reg_def_id=revoc_reg_def_id)

    # TODO: do not duplicate seqNo here
    # doing this now just for backward-compatibility
    txn_data = deepcopy(txn_data)
    txn_data[f.SEQ_NO.nm] = seq_no
    txn_data[TXN_TIME] = txn_time
    value_bytes = encode_state_value(txn_data, seq_no, txn_time)
    return path, value_bytes


def prepare_get_claim_def_for_state(reply):
    origin = reply.get(ORIGIN)
    schema_seq_no = reply.get(REF)
    if schema_seq_no is None:
        raise ValueError("'{}' field is absent, "
                         "but it must contain schema seq no".format(REF))

    signature_type = reply.get(SIGNATURE_TYPE, 'CL')
    path = make_state_path_for_claim_def(origin, schema_seq_no, signature_type)
    seq_no = reply[f.SEQ_NO.nm]

    value_bytes = None
    data = reply.get(DATA)
    if data is not None:
        txn_time = reply[TXN_TIME]
        value_bytes = encode_state_value(data, seq_no, txn_time)
    return path, value_bytes


def prepare_get_revoc_def_for_state(reply):
    author_did = reply.get(f.IDENTIFIER.nm)
    cred_def_id = reply.get(DATA).get(CRED_DEF_ID)
    revoc_def_type = reply.get(DATA).get(REVOC_TYPE)
    revoc_def_tag = reply.get(DATA).get(TAG)
    assert author_did
    assert cred_def_id
    assert revoc_def_type
    assert revoc_def_tag
    path = make_state_path_for_revoc_def(author_did,
                                         cred_def_id,
                                         revoc_def_type,
                                         revoc_def_tag)
    seq_no = reply[f.SEQ_NO.nm]
    txn_time = reply[TXN_TIME]
    assert seq_no
    assert txn_time
    value_bytes = encode_state_value(reply[DATA], seq_no, txn_time)
    return path, value_bytes


def prepare_get_revoc_reg_entry_for_state(reply):
    revoc_reg_def_id = reply.get(DATA).get(REVOC_REG_DEF_ID)
    assert revoc_reg_def_id
    path = make_state_path_for_revoc_reg_entry(revoc_reg_def_id=revoc_reg_def_id)

    seq_no = reply[f.SEQ_NO.nm]
    txn_time = reply[TXN_TIME]
    assert seq_no
    assert txn_time
    value_bytes = encode_state_value(reply[DATA], seq_no, txn_time)
    return path, value_bytes


def prepare_get_revoc_reg_entry_accum_for_state(reply):
    revoc_reg_def_id = reply.get(DATA).get(REVOC_REG_DEF_ID)
    seq_no = reply[f.SEQ_NO.nm]
    txn_time = reply[TXN_TIME]
    assert revoc_reg_def_id
    assert seq_no
    assert txn_time
    path = make_state_path_for_revoc_reg_entry_accum(revoc_reg_def_id=revoc_reg_def_id)

    value_bytes = encode_state_value(reply[DATA], seq_no, txn_time)
    return path, value_bytes


def prepare_schema_for_state(txn):
    origin = get_from(txn)
    txn_data = get_payload_data(txn)
    data = deepcopy(txn_data.get(DATA))
    schema_name = data.pop(NAME)
    schema_version = data.pop(VERSION)
    path = make_state_path_for_schema(origin, schema_name, schema_version)
    seq_no = get_seq_no(txn)
    txn_time = get_txn_time(txn)
    value_bytes = encode_state_value(data, seq_no, txn_time)
    return path, value_bytes


def prepare_get_schema_for_state(reply):
    origin = reply.get(TARGET_NYM)
    data = reply[DATA].copy()
    schema_name = data.pop(NAME)
    schema_version = data.pop(VERSION)
    path = make_state_path_for_schema(origin, schema_name, schema_version)
    value_bytes = None
    if len(data) != 0:
        seq_no = reply[f.SEQ_NO.nm]
        txn_time = reply[TXN_TIME]
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


def parse_attr_txn(txn_data):
    attr_type, attr = _extract_attr_typed_value(txn_data)

    if attr_type == RAW:
        data = attrib_raw_data_serializer.deserialize(attr)
        # To exclude user-side formatting issues
        re_raw = attrib_raw_data_serializer.serialize(data,
                                                      toBytes=False)
        key, _ = data.popitem()
        return attr_type, key, re_raw
    if attr_type == ENC:
        return attr_type, attr, attr
    if attr_type == HASH:
        return attr_type, attr, None


def prepare_get_attr_for_state(reply):
    nym = reply[TARGET_NYM]
    attr_type, attr_key = _extract_attr_typed_value(reply)
    data = reply.get(DATA)
    if data:
        reply = reply.copy()
        data = reply.pop(DATA)
        reply[attr_type] = data

        assert reply[TYPE] == GET_ATTR
        attr_type, attr_key, value = parse_attr_txn(reply)
        hashed_value = hash_of(value) if value else ''
        seq_no = reply[f.SEQ_NO.nm]
        txn_time = reply[TXN_TIME]
        value_bytes = encode_state_value(hashed_value, seq_no, txn_time)
        path = make_state_path_for_attr(nym, attr_key, attr_type == HASH)

        return attr_type, path, value, hashed_value, value_bytes

    if attr_type == ENC:
        attr_key = hash_of(attr_key)

    path = make_state_path_for_attr(nym, attr_key,
                                    attr_type == HASH or attr_type == ENC)
    return attr_type, path, None, None, None


def _extract_attr_typed_value(txn_data):
    """
    ATTR and GET_ATTR can have one of 'raw', 'enc' and 'hash' fields.
    This method checks which of them presents and return it's name
    and value in it.
    """
    existing_keys = [key for key in ALL_ATR_KEYS if key in txn_data]
    if len(existing_keys) == 0:
        raise ValueError("ATTR should have one of the following fields: {}"
                         .format(ALL_ATR_KEYS))
    if len(existing_keys) > 1:
        raise ValueError("ATTR should have only one of the following fields: {}"
                         .format(ALL_ATR_KEYS))
    existing_key = existing_keys[0]
    return existing_key, txn_data[existing_key]
