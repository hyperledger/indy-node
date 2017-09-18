import pytest
from plenum.common.constants import TXN_TYPE, TARGET_NYM, RAW, DATA, ORIGIN, \
    IDENTIFIER, NAME, VERSION, ROLE, VERKEY, KeyValueStorageType, \
    STATE_PROOF, ROOT_HASH, MULTI_SIGNATURE, PROOF_NODES
from plenum.common.types import f
from state.pruning_state import PruningState
from storage.kv_in_memory import KeyValueStorageInMemory

from sovrin_common.constants import \
    ATTRIB, REF, SIGNATURE_TYPE, CLAIM_DEF, SCHEMA
from sovrin_common.types import Request
from sovrin_node.persistence.attribute_store import AttributeStore
from sovrin_node.persistence.idr_cache import IdrCache
from sovrin_node.server.domain_req_handler import DomainReqHandler
import base58
from plenum.bls.bls_store import BlsStore


def make_request_handler():
    state = PruningState(KeyValueStorageInMemory())
    cache = IdrCache('Cache', KeyValueStorageInMemory())
    attr_store = AttributeStore(KeyValueStorageInMemory())
    bls_store = BlsStore(keyValueType=KeyValueStorageType.Memory,
                         dataLocation=None,
                         keyValueStorageName="BlsInMemoryStore")
    return DomainReqHandler(ledger=None,
                            state=state,
                            requestProcessor=None,
                            idrCache=cache,
                            attributeStore=attr_store,
                            bls_store=bls_store)


def extract_proof(result):
    proof = result[STATE_PROOF]
    assert proof
    root_hash = proof[ROOT_HASH]
    assert root_hash
    assert proof[PROOF_NODES]
    # TODO: check multi singature
    # multi_sign = result[STATE_PROOF][MULTI_SIGNATURE]
    # assert multi_sign
    return proof


def test_state_proofs_for_get_attr():
    # Creating required structures
    req_handler = make_request_handler()

    # Adding attribute
    nym = 'Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv'
    attr_key = 'last_name'
    raw_attribute = '{"last_name": "Anderson"}'
    seq_no = 0
    txn = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: nym,
        RAW: raw_attribute,
        f.SEQ_NO.nm: seq_no,
    }
    req_handler._addAttr(txn)
    req_handler.state.commit()

    # Getting attribute
    get_request = Request(
        operation={
            TARGET_NYM: nym,
            RAW: 'last_name'
        }
    )
    result = req_handler.handleGetAttrsReq(get_request, 'Sender')

    proof = extract_proof(result)
    attr_value = result[DATA]
    assert attr_value == raw_attribute

    # Verifying signed state proof
    path = req_handler._makeAttrPath(nym, attr_key)
    encoded_value = req_handler._encodeValue(req_handler._hashOf(attr_value),
                                             seq_no)

    proof_nodes = base58.b58decode(proof[PROOF_NODES])
    root_hash = base58.b58decode(proof[ROOT_HASH])
    verified = req_handler.state.verify_state_proof(
        root_hash,
        path,
        encoded_value,
        proof_nodes,
        serialized=True
    )
    assert verified


def test_state_proofs_for_get_claim_def():
    # Creating required structures
    req_handler = make_request_handler()

    # Adding claim def
    nym = 'Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv'

    seq_no = 0
    schema_seqno = 0
    signature_type = 'CL'
    key_components = '{"key_components": []}'

    txn = {
        IDENTIFIER: nym,
        TXN_TYPE: CLAIM_DEF,
        TARGET_NYM: nym,
        REF: schema_seqno,
        f.SEQ_NO.nm: seq_no,
        DATA: key_components
    }

    req_handler._addClaimDef(txn)
    req_handler.state.commit()

    # Getting claim def
    request = Request(
        operation={
            IDENTIFIER: nym,
            ORIGIN: nym,
            REF: schema_seqno,
            SIGNATURE_TYPE: signature_type
        }
    )

    result = req_handler.handleGetClaimDefReq(request, 'Sender')
    proof = extract_proof(result)
    assert result[DATA] == key_components

    # Verifying signed state proof
    path = req_handler._makeClaimDefPath(nym, schema_seqno, signature_type)
    encoded_value = req_handler._encodeValue(key_components,
                                             seq_no)
    proof_nodes = base58.b58decode(proof[PROOF_NODES])
    root_hash = base58.b58decode(proof[ROOT_HASH])
    verified = req_handler.state.verify_state_proof(
        root_hash,
        path,
        encoded_value,
        proof_nodes,
        serialized=True
    )
    assert verified


def test_state_proofs_for_get_schema():
    # Creating required structures
    req_handler = make_request_handler()

    # Adding schema
    nym = 'Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv'

    seq_no = 0

    schema_name = "schema_a"
    schema_version = "1.0"
    # data = '{"name": "schema_a", "version": "1.0"}'
    schema_key = {NAME: schema_name, VERSION: schema_version}
    data = {**schema_key, "Some_Attr": "Attr1"}
    txn = {
        TXN_TYPE: SCHEMA,
        IDENTIFIER: nym,
        f.SEQ_NO.nm: seq_no,
        DATA: data
    }

    req_handler._addSchema(txn)
    req_handler.state.commit()

    # Getting schema
    request = Request(
        operation={
            TARGET_NYM: nym,
            DATA: schema_key
        }
    )

    result = req_handler.handleGetSchemaReq(request, 'Sender')
    proof = extract_proof(result)
    assert result[DATA] == data

    # Verifying signed state proof
    path = req_handler._makeSchemaPath(nym, schema_name, schema_version)
    encoded_value = req_handler._encodeValue(data,
                                             seq_no)
    proof_nodes = base58.b58decode(proof[PROOF_NODES])
    root_hash = base58.b58decode(proof[ROOT_HASH])
    verified = req_handler.state.verify_state_proof(
        root_hash,
        path,
        encoded_value,
        proof_nodes,
        serialized=True
    )
    assert verified


def test_state_proofs_for_get_nym():
    # Creating required structures
    req_handler = make_request_handler()
    nym = 'Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv'
    role = "2"
    verkey = "~7TYfekw4GUagBnBVCqPjiC"
    # Adding nym
    data = {
        f.IDENTIFIER.nm: nym,
        ROLE: role,
        VERKEY: verkey,
        f.SEQ_NO.nm: 0
    }
    req_handler.updateNym(nym, data)
    req_handler.state.commit()
    # Getting nym
    request = Request(
        operation={
            TARGET_NYM: nym
        }
    )
    result = req_handler.handleGetNymReq(request, "Sender")
    proof = extract_proof(result)
    # Verifying signed state proof
    path = req_handler.nym_to_state_key(nym)
    encoded_value = req_handler.stateSerializer.serialize(data)
    proof_nodes = base58.b58decode(proof[PROOF_NODES])
    root_hash = base58.b58decode(proof[ROOT_HASH])
    verified = req_handler.state.verify_state_proof(
        root_hash,
        path,
        encoded_value,
        proof_nodes,
        serialized=True
    )
    assert verified
