import pytest
from plenum.common.constants import TXN_TYPE, TARGET_NYM, RAW, DATA
from plenum.common.types import f
from state.pruning_state import PruningState
from storage.kv_in_memory import KeyValueStorageInMemory

from sovrin_common.constants import \
    ATTRIB, STATE_PROOF, ROOT_HASH, MULTI_SIGNATURE, PROOF_NODES
from sovrin_common.types import Request
from sovrin_node.persistence.attribute_store import AttributeStore
from sovrin_node.persistence.idr_cache import IdrCache
from sovrin_node.server.domain_req_handler import DomainReqHandler


def make_request_handler():
    state = PruningState(KeyValueStorageInMemory())
    cache = IdrCache('Cache', KeyValueStorageInMemory())
    attr_store = AttributeStore(KeyValueStorageInMemory())
    return DomainReqHandler(ledger=None,
                            state=state,
                            requestProcessor=None,
                            idrCache=cache,
                            attributeStore=attr_store)


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
    request = Request(
        operation={
            TARGET_NYM: nym,
            RAW: 'last_name'
        }
    )
    result = req_handler.handleGetAttrsReq(request, 'Sender')
    assert result[STATE_PROOF]
    root_hash = result[STATE_PROOF][ROOT_HASH]
    # TODO: check multi singature
    # multi_sign = result[STATE_PROOF][MULTI_SIGNATURE]
    proof = result[STATE_PROOF][PROOF_NODES]
    assert root_hash
    # assert multi_sign
    assert proof
    attr_value = result[DATA]
    assert attr_value == raw_attribute

    # Verifying signed state proof
    path = req_handler._makeAttrPath(nym, attr_key)
    encoded_value = req_handler._encodeValue(req_handler._hashOf(attr_value),
                                             seq_no)
    verified = req_handler.state.verify_state_proof(
        root_hash,
        path,
        encoded_value,
        proof
    )
    assert verified
