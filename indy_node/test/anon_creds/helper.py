from plenum.common.types import f

from plenum.common.constants import STATE_PROOF, ROOT_HASH, MULTI_SIGNATURE, PROOF_NODES, MULTI_SIGNATURE_SIGNATURE, \
    MULTI_SIGNATURE_PARTICIPANTS, MULTI_SIGNATURE_VALUE, MULTI_SIGNATURE_VALUE_LEDGER_ID, \
    MULTI_SIGNATURE_VALUE_STATE_ROOT, MULTI_SIGNATURE_VALUE_TXN_ROOT, MULTI_SIGNATURE_VALUE_POOL_STATE_ROOT, \
    MULTI_SIGNATURE_VALUE_TIMESTAMP, TYPE, DATA, TXN_TIME, TXN_PAYLOAD, TXN_PAYLOAD_METADATA, TXN_PAYLOAD_METADATA_FROM, \
    TXN_PAYLOAD_DATA, TXN_METADATA, TXN_METADATA_SEQ_NO, TXN_METADATA_TIME
from indy_common.constants import VALUE, GET_REVOC_REG_DEF, GET_REVOC_REG, GET_REVOC_REG_DELTA, \
    ACCUM_TO, ISSUED, STATE_PROOF_FROM, ACCUM_FROM
from common.serializers.serialization import state_roots_serializer, proof_nodes_serializer
from state.pruning_state import PruningState
from indy_common.state import domain


def add_txn_specific_fileds(result):
    result[TXN_PAYLOAD] = {TXN_PAYLOAD_METADATA: {TXN_PAYLOAD_METADATA_FROM: result[f.IDENTIFIER.nm]}}
    result[TXN_PAYLOAD][TXN_PAYLOAD_DATA] = result[TXN_PAYLOAD_DATA]
    result[TXN_METADATA] = {TXN_METADATA_SEQ_NO: result[TXN_METADATA_SEQ_NO]}
    result[TXN_METADATA][TXN_METADATA_TIME] = result[TXN_METADATA_TIME]


def prepare_for_state(result):
    request_type = result[TYPE]
    add_txn_specific_fileds(result)
    if request_type == GET_REVOC_REG_DEF:
        return domain.prepare_revoc_def_for_state(result)
    if request_type == GET_REVOC_REG:
        return domain.prepare_revoc_reg_entry_accum_for_state(result)
    if request_type == GET_REVOC_REG_DELTA:
        if ISSUED in result[DATA][VALUE]:
            return domain.prepare_revoc_reg_entry_for_state(result)
        else:
            return domain.prepare_revoc_reg_entry_accum_for_state(result)
    raise ValueError("Cannot make state key for "
                     "request of type {}"
                     .format(request_type))


def validate_proof(result):
    """
    Validates state proof
    """
    state_root_hash = result[STATE_PROOF]['root_hash']
    state_root_hash = state_roots_serializer.deserialize(state_root_hash)
    proof_nodes = result[STATE_PROOF]['proof_nodes']
    if isinstance(proof_nodes, str):
        proof_nodes = proof_nodes.encode()
    proof_nodes = proof_nodes_serializer.deserialize(proof_nodes)
    key, value = prepare_for_state(result)
    valid = PruningState.verify_state_proof(state_root_hash,
                                            key,
                                            value,
                                            proof_nodes,
                                            serialized=True)
    return valid


def check_valid_proof(reply):
    result = reply['result']
    assert STATE_PROOF in result

    state_proof = result[STATE_PROOF]
    assert ROOT_HASH in state_proof
    assert state_proof[ROOT_HASH]
    assert PROOF_NODES in state_proof
    assert state_proof[PROOF_NODES]
    assert MULTI_SIGNATURE in state_proof

    multi_sig = state_proof[MULTI_SIGNATURE]
    assert multi_sig
    assert multi_sig[MULTI_SIGNATURE_PARTICIPANTS]
    assert multi_sig[MULTI_SIGNATURE_SIGNATURE]
    assert MULTI_SIGNATURE_VALUE in multi_sig

    multi_sig_value = multi_sig[MULTI_SIGNATURE_VALUE]
    assert MULTI_SIGNATURE_VALUE_LEDGER_ID in multi_sig_value
    assert multi_sig_value[MULTI_SIGNATURE_VALUE_LEDGER_ID]
    assert MULTI_SIGNATURE_VALUE_STATE_ROOT in multi_sig_value
    assert multi_sig_value[MULTI_SIGNATURE_VALUE_STATE_ROOT]
    assert MULTI_SIGNATURE_VALUE_TXN_ROOT in multi_sig_value
    assert multi_sig_value[MULTI_SIGNATURE_VALUE_TXN_ROOT]
    assert MULTI_SIGNATURE_VALUE_POOL_STATE_ROOT in multi_sig_value
    assert multi_sig_value[MULTI_SIGNATURE_VALUE_POOL_STATE_ROOT]
    assert MULTI_SIGNATURE_VALUE_TIMESTAMP in multi_sig_value
    assert multi_sig_value[MULTI_SIGNATURE_VALUE_TIMESTAMP]
    if result[TYPE] == GET_REVOC_REG_DELTA:
        if STATE_PROOF_FROM in result[DATA] and result[DATA][STATE_PROOF_FROM]:
            reply_from = {DATA: result[DATA][VALUE][ACCUM_FROM],
                          STATE_PROOF: result[DATA][STATE_PROOF_FROM],
                          TYPE: result[TYPE],
                          f.IDENTIFIER.nm: result[f.IDENTIFIER.nm],
                          f.SEQ_NO.nm: result[DATA][VALUE][f.SEQ_NO.nm + 'From'],
                          TXN_TIME: result[DATA][VALUE][TXN_TIME + 'From']
                          }
            assert validate_proof(reply_from)
        reply_to = {DATA: result['data'][VALUE][ACCUM_TO],
                    STATE_PROOF: result[STATE_PROOF],
                    TYPE: result[TYPE],
                    f.IDENTIFIER.nm: result[f.IDENTIFIER.nm],
                    f.SEQ_NO.nm: result[f.SEQ_NO.nm],
                    TXN_TIME: result[TXN_TIME]
                    }
        assert validate_proof(reply_to)
    else:
        assert validate_proof(result)
