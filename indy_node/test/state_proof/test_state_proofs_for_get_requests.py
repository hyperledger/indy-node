import base64
import time

import base58
import pytest
from common.serializers import serialization
from common.serializers.serialization import state_roots_serializer
from crypto.bls.bls_multi_signature import MultiSignature, MultiSignatureValue
from plenum.bls.bls_store import BlsStore
from plenum.common.constants import TXN_TYPE, TARGET_NYM, RAW, DATA, ORIGIN, \
    IDENTIFIER, NAME, VERSION, ROLE, VERKEY, KeyValueStorageType, \
    STATE_PROOF, ROOT_HASH, MULTI_SIGNATURE, PROOF_NODES, TXN_TIME, CURRENT_PROTOCOL_VERSION, DOMAIN_LEDGER_ID
from plenum.common.types import f
from indy_common.constants import \
    ATTRIB, REF, SIGNATURE_TYPE, CLAIM_DEF, SCHEMA
from indy_common.types import Request
from indy_node.persistence.attribute_store import AttributeStore
from indy_node.persistence.idr_cache import IdrCache
from indy_node.server.domain_req_handler import DomainReqHandler
from plenum.common.util import get_utc_epoch
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
    cache = IdrCache('Cache', KeyValueStorageInMemory())
    attr_store = AttributeStore(KeyValueStorageInMemory())
    return DomainReqHandler(ledger=None,
                            state=state,
                            config=None,
                            requestProcessor=None,
                            idrCache=cache,
                            attributeStore=attr_store,
                            bls_store=bls_store)


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
    txn = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: nym,
        RAW: raw_attribute,
        f.SEQ_NO.nm: seq_no,
        TXN_TIME: txn_time,
    }
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

    schema_seqno = 0
    signature_type = 'CL'
    key_components = '{"key_components": []}'

    txn = {
        IDENTIFIER: nym,
        TXN_TYPE: CLAIM_DEF,
        TARGET_NYM: nym,
        REF: schema_seqno,
        f.SEQ_NO.nm: seq_no,
        DATA: key_components,
        TXN_TIME: txn_time,
    }

    request_handler._addClaimDef(txn)
    request_handler.state.commit()
    multi_sig = save_multi_sig(request_handler)

    # Getting claim def
    request = Request(
        operation={
            IDENTIFIER: nym,
            ORIGIN: nym,
            REF: schema_seqno,
            SIGNATURE_TYPE: signature_type
        },
        signatures={},
        protocolVersion=CURRENT_PROTOCOL_VERSION
    )

    result = request_handler.handleGetClaimDefReq(request)
    proof = extract_proof(result, multi_sig)
    assert result[DATA] == key_components

    # Verifying signed state proof
    path = domain.make_state_path_for_claim_def(nym, schema_seqno,
                                                signature_type)
    assert is_proof_verified(request_handler,
                             proof, path,
                             key_components, seq_no, txn_time)


def test_state_proofs_for_get_schema(request_handler):
    # Adding schema
    nym = 'Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv'

    seq_no = 0
    txn_time = int(time.time())

    schema_name = "schema_a"
    schema_version = "1.0"
    # data = '{"name": "schema_a", "version": "1.0"}'
    schema_key = {NAME: schema_name, VERSION: schema_version}
    data = {**schema_key, "Some_Attr": "Attr1"}
    txn = {
        TXN_TYPE: SCHEMA,
        IDENTIFIER: nym,
        f.SEQ_NO.nm: seq_no,
        DATA: data,
        TXN_TIME: txn_time,
    }

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
    result[DATA].pop(NAME)
    result[DATA].pop(VERSION)
    assert result[DATA] == data

    # Verifying signed state proof
    path = domain.make_state_path_for_schema(nym, schema_name, schema_version)
    assert is_proof_verified(request_handler,
                             proof, path,
                             data, seq_no, txn_time)


def test_state_proofs_for_get_nym(request_handler):
    nym = 'Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv'
    role = "2"
    verkey = "~7TYfekw4GUagBnBVCqPjiC"
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
    request_handler.updateNym(nym, data)
    request_handler.state.commit()
    multi_sig = save_multi_sig(request_handler)

    # Getting nym
    request = Request(
        operation={
            TARGET_NYM: nym
        },
        signatures={},
        protocolVersion=CURRENT_PROTOCOL_VERSION
    )
    result = request_handler.handleGetNymReq(request)
    proof = extract_proof(result, multi_sig)

    # Verifying signed state proof
    path = request_handler.nym_to_state_key(nym)
    encoded_value = request_handler.stateSerializer.serialize(data)
    proof_nodes = base64.b64decode(proof[PROOF_NODES])
    root_hash = base58.b58decode(proof[ROOT_HASH])
    verified = request_handler.state.verify_state_proof(
        root_hash,
        path,
        encoded_value,
        proof_nodes,
        serialized=True
    )
    assert verified


def test_no_state_proofs_if_protocol_version_less(request_handler):
    nym = 'Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv'
    role = "2"
    verkey = "~7TYfekw4GUagBnBVCqPjiC"
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
    request_handler.updateNym(nym, data)
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
