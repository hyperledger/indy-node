import base64
import random

import time

import base58
import pytest
from common.serializers import serialization
from common.serializers.serialization import state_roots_serializer, domain_state_serializer
from crypto.bls.bls_multi_signature import MultiSignature, MultiSignatureValue
from indy_common.authorize.auth_constraints import ConstraintsSerializer
from indy_common.authorize.auth_map import auth_map
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from plenum.bls.bls_store import BlsStore
from plenum.common.constants import TXN_TYPE, TARGET_NYM, RAW, DATA, \
    IDENTIFIER, NAME, VERSION, ROLE, VERKEY, KeyValueStorageType, \
    STATE_PROOF, ROOT_HASH, MULTI_SIGNATURE, PROOF_NODES, TXN_TIME, CURRENT_PROTOCOL_VERSION, DOMAIN_LEDGER_ID
from plenum.common.txn_util import reqToTxn, append_txn_metadata, append_payload_metadata
from plenum.common.types import f
from indy_common.constants import \
    ATTRIB, CLAIM_DEF, SCHEMA, CLAIM_DEF_FROM, CLAIM_DEF_SCHEMA_REF, CLAIM_DEF_SIGNATURE_TYPE, \
    CLAIM_DEF_PUBLIC_KEYS, CLAIM_DEF_TAG, SCHEMA_NAME, SCHEMA_VERSION, SCHEMA_ATTR_NAMES, LOCAL_AUTH_POLICY, \
    CONFIG_LEDGER_AUTH_POLICY
from indy_common.types import Request
from indy_node.persistence.attribute_store import AttributeStore
from indy_node.persistence.idr_cache import IdrCache
from indy_node.server.domain_req_handler import DomainReqHandler
from plenum.common.util import get_utc_epoch, friendlyToRaw, rawToFriendly, \
    friendlyToHex, hexToFriendly
from plenum.test.testing_utils import FakeSomething
from state.pruning_state import PruningState
from storage.kv_in_memory import KeyValueStorageInMemory
from indy_common.state import domain


@pytest.fixture()
def bls_store():
    return BlsStore(key_value_type=KeyValueStorageType.Memory,
                    data_location=None,
                    key_value_storage_name="BlsInMemoryStore",
                    serializer=serialization.multi_sig_store_serializer)


@pytest.fixture()
def request_handler(bls_store):
    state = PruningState(KeyValueStorageInMemory())
    config_state = PruningState(KeyValueStorageInMemory())
    state_serializer = ConstraintsSerializer(domain_state_serializer)
    cache = IdrCache('Cache', KeyValueStorageInMemory())
    attr_store = AttributeStore(KeyValueStorageInMemory())
    write_req_validator = WriteRequestValidator(config=FakeSomething(authPolicy=CONFIG_LEDGER_AUTH_POLICY),
                                                auth_map=auth_map,
                                                cache=cache,
                                                config_state=config_state,
                                                state_serializer=state_serializer)
    return DomainReqHandler(ledger=None,
                            state=state,
                            config=None,
                            requestProcessor=None,
                            idrCache=cache,
                            attributeStore=attr_store,
                            bls_store=bls_store,
                            write_req_validator=write_req_validator,
                            ts_store=None)


def extract_proof(result, expected_multi_sig):
    proof = result[STATE_PROOF]
    assert proof
    assert proof[ROOT_HASH]
    assert proof[PROOF_NODES]
    multi_sign = proof[MULTI_SIGNATURE]
    assert multi_sign
    assert multi_sign == expected_multi_sig
    return proof


def save_multi_sig(request_handler):
    multi_sig_value = MultiSignatureValue(ledger_id=DOMAIN_LEDGER_ID,
                                          state_root_hash=state_roots_serializer.serialize(
                                              bytes(request_handler.state.committedHeadHash)),
                                          txn_root_hash='2' * 32,
                                          pool_state_root_hash='1' * 32,
                                          timestamp=get_utc_epoch())
    multi_sig = MultiSignature('0' * 32, ['Alpha', 'Beta', 'Gamma'], multi_sig_value)
    request_handler.bls_store.put(multi_sig)
    return multi_sig.as_dict()


def is_proof_verified(request_handler,
                      proof, path,
                      value, seq_no, txn_time, ):
    encoded_value = domain.encode_state_value(value, seq_no, txn_time)
    proof_nodes = base64.b64decode(proof[PROOF_NODES])
    root_hash = base58.b58decode(proof[ROOT_HASH])
    verified = request_handler.state.verify_state_proof(
        root_hash,
        path,
        encoded_value,
        proof_nodes,
        serialized=True
    )
    return verified


def test_state_proofs_for_get_attr(request_handler):
    # Adding attribute
    nym = 'Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv'
    attr_key = 'last_name'
    raw_attribute = '{"last_name":"Anderson"}'
    seq_no = 0
    txn_time = int(time.time())
    identifier = "6ouriXMZkLeHsuXrN1X1fd"
    txn = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: nym,
        RAW: raw_attribute,
    }
    txn = append_txn_metadata(reqToTxn(Request(operation=txn,
                                               protocolVersion=CURRENT_PROTOCOL_VERSION,
                                               identifier=identifier)),
                              seq_no=seq_no, txn_time=txn_time)
    request_handler._addAttr(txn)
    request_handler.state.commit()
    multi_sig = save_multi_sig(request_handler)

    # Getting attribute
    get_request = Request(
        operation={
            TARGET_NYM: nym,
            RAW: 'last_name'
        },
        signatures={},
        protocolVersion=CURRENT_PROTOCOL_VERSION
    )
    result = request_handler.handleGetAttrsReq(get_request)

    proof = extract_proof(result, multi_sig)
    attr_value = result[DATA]
    assert attr_value == raw_attribute

    # Verifying signed state proof
    path = domain.make_state_path_for_attr(nym, attr_key)
    assert is_proof_verified(request_handler,
                             proof, path,
                             domain.hash_of(attr_value), seq_no, txn_time)


def test_state_proofs_for_get_claim_def(request_handler):
    # Adding claim def
    nym = 'Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv'

    seq_no = 0
    txn_time = int(time.time())
    identifier = "6ouriXMZkLeHsuXrN1X1fd"

    schema_seqno = 0
    signature_type = 'CL'
    key_components = '{"key_components": []}'
    tag = 'tag1'

    txn = {
        TXN_TYPE: CLAIM_DEF,
        TARGET_NYM: nym,
        CLAIM_DEF_SCHEMA_REF: schema_seqno,
        CLAIM_DEF_PUBLIC_KEYS: key_components,
        CLAIM_DEF_TAG: tag
    }
    txn = append_txn_metadata(reqToTxn(Request(operation=txn,
                                               protocolVersion=CURRENT_PROTOCOL_VERSION,
                                               identifier=identifier)),
                              seq_no=seq_no, txn_time=txn_time)
    txn = append_payload_metadata(txn, frm=nym)

    request_handler._addClaimDef(txn)
    request_handler.state.commit()
    multi_sig = save_multi_sig(request_handler)

    # Getting claim def
    request = Request(
        operation={
            IDENTIFIER: nym,
            CLAIM_DEF_FROM: nym,
            CLAIM_DEF_SCHEMA_REF: schema_seqno,
            CLAIM_DEF_SIGNATURE_TYPE: signature_type,
            CLAIM_DEF_TAG: tag
        },
        signatures={},
        protocolVersion=CURRENT_PROTOCOL_VERSION
    )

    result = request_handler.handleGetClaimDefReq(request)
    proof = extract_proof(result, multi_sig)
    assert result[DATA] == key_components

    # Verifying signed state proof
    path = domain.make_state_path_for_claim_def(nym, schema_seqno,
                                                signature_type, tag)
    assert is_proof_verified(request_handler,
                             proof, path,
                             key_components, seq_no, txn_time)


def test_state_proofs_for_get_schema(request_handler):
    # Adding schema
    nym = 'Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv'

    seq_no = 0
    txn_time = int(time.time())
    identifier = "6ouriXMZkLeHsuXrN1X1fd"

    schema_name = "schema_a"
    schema_version = "1.0"
    # data = '{"name": "schema_a", "version": "1.0"}'
    schema_key = {SCHEMA_NAME: schema_name,
                  SCHEMA_VERSION: schema_version}
    data = {**schema_key,
            SCHEMA_ATTR_NAMES: ["Some_Attr", "Attr1"]}
    txn = {
        TXN_TYPE: SCHEMA,
        DATA: data,
    }
    txn = append_txn_metadata(reqToTxn(Request(operation=txn,
                                               protocolVersion=CURRENT_PROTOCOL_VERSION,
                                               identifier=identifier)),
                              seq_no=seq_no, txn_time=txn_time)
    txn = append_payload_metadata(txn, frm=nym)

    request_handler._addSchema(txn)
    request_handler.state.commit()
    multi_sig = save_multi_sig(request_handler)

    # Getting schema
    request = Request(
        operation={
            TARGET_NYM: nym,
            DATA: schema_key
        },
        signatures={},
        protocolVersion=CURRENT_PROTOCOL_VERSION
    )

    result = request_handler.handleGetSchemaReq(request)
    proof = extract_proof(result, multi_sig)
    assert result[DATA] == data

    data.pop(NAME)
    data.pop(VERSION)

    # Verifying signed state proof
    path = domain.make_state_path_for_schema(nym, schema_name, schema_version)
    assert is_proof_verified(request_handler,
                             proof, path,
                             data, seq_no, txn_time)


def prep_multi_sig(request_handler, nym, role, verkey, seq_no):
    txn_time = int(time.time())
    identifier = "6ouriXMZkLeHsuXrN1X1fd"

    # Adding nym
    data = {
        f.IDENTIFIER.nm: nym,
        ROLE: role,
        VERKEY: verkey,
        f.SEQ_NO.nm: seq_no,
        TXN_TIME: txn_time,
    }
    txn = append_txn_metadata(reqToTxn(Request(operation=data,
                                               protocolVersion=CURRENT_PROTOCOL_VERSION,
                                               identifier=identifier)),
                              seq_no=seq_no, txn_time=txn_time)
    txn = append_payload_metadata(txn, frm=nym)
    request_handler.updateNym(nym, txn)
    request_handler.state.commit()
    multi_sig = save_multi_sig(request_handler)
    return data, multi_sig


def get_nym_verify_proof(request_handler, nym, data, multi_sig):
    request = Request(
        operation={
            TARGET_NYM: nym
        },
        signatures={},
        protocolVersion=CURRENT_PROTOCOL_VERSION
    )
    result = request_handler.handleGetNymReq(request)
    proof = extract_proof(result, multi_sig)

    assert proof
    if data:
        assert result[DATA]
        result_data = request_handler.stateSerializer.deserialize(result[DATA])
        result_data.pop(TARGET_NYM, None)
        assert result_data == data

    # Verifying signed state proof
    path = request_handler.nym_to_state_key(nym)
    # If the value does not exist, serialisation should be null and
    # verify_state_proof needs to be given null (None). This is done to
    # differentiate between absence of value and presence of empty string value
    serialised_value = request_handler.stateSerializer.serialize(data) if data else None
    proof_nodes = base64.b64decode(proof[PROOF_NODES])
    root_hash = base58.b58decode(proof[ROOT_HASH])
    return request_handler.state.verify_state_proof(
        root_hash,
        path,
        serialised_value,
        proof_nodes,
        serialized=True
    )


def test_state_proofs_for_get_nym(request_handler):
    nym = 'Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv'
    role = "2"
    verkey = "~7TYfekw4GUagBnBVCqPjiC"
    seq_no = 1
    # Check for existing nym
    data, multi_sig = prep_multi_sig(request_handler, nym, role, verkey, seq_no)
    assert get_nym_verify_proof(request_handler, nym, data, multi_sig)

    # Shuffle the bytes of nym
    h = list(friendlyToHex(nym))
    random.shuffle(h)
    garbled_nym = hexToFriendly(bytes(h))
    data[f.IDENTIFIER.nm] = garbled_nym
    # `garbled_nym` does not exist, proof should verify but data is null
    assert get_nym_verify_proof(request_handler, garbled_nym, None, multi_sig)


def test_no_state_proofs_if_protocol_version_less(request_handler):
    nym = 'Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv'
    role = "2"
    verkey = "~7TYfekw4GUagBnBVCqPjiC"
    identifier = "6ouriXMZkLeHsuXrN1X1fd"

    seq_no = 0
    txn_time = int(time.time())
    # Adding nym
    data = {
        f.IDENTIFIER.nm: nym,
        ROLE: role,
        VERKEY: verkey,
        f.SEQ_NO.nm: seq_no,
        TXN_TIME: txn_time,
    }
    txn = append_txn_metadata(reqToTxn(Request(operation=data,
                                               protocolVersion=CURRENT_PROTOCOL_VERSION,
                                               identifier=identifier)),
                              seq_no=seq_no, txn_time=txn_time)
    txn = append_payload_metadata(txn, frm=nym)
    request_handler.updateNym(nym, txn)
    request_handler.state.commit()
    multi_sig = save_multi_sig(request_handler)

    # Getting nym
    request = Request(
        operation={
            TARGET_NYM: nym
        },
        signatures={}
    )
    result = request_handler.handleGetNymReq(request)
    assert STATE_PROOF not in result
