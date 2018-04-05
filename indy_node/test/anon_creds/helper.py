from plenum.common.constants import STATE_PROOF, ROOT_HASH, MULTI_SIGNATURE, PROOF_NODES, MULTI_SIGNATURE_SIGNATURE, \
    MULTI_SIGNATURE_PARTICIPANTS, MULTI_SIGNATURE_VALUE, MULTI_SIGNATURE_VALUE_LEDGER_ID, \
    MULTI_SIGNATURE_VALUE_STATE_ROOT, MULTI_SIGNATURE_VALUE_TXN_ROOT, MULTI_SIGNATURE_VALUE_POOL_STATE_ROOT, \
    MULTI_SIGNATURE_VALUE_TIMESTAMP, TYPE, DATA
from indy_common.constants import VALUE, GET_REVOC_REG_DEF, GET_REVOC_REG, GET_REVOC_REG_DELTA, \
    ACCUM_FROM, ACCUM_TO, STATE_PROOF_FROM, ISSUED
from common.serializers.serialization import state_roots_serializer, proof_nodes_serializer
from state.pruning_state import PruningState
from indy_common.state import domain


def prepare_for_state(result):
    request_type = result[TYPE]
    if request_type == GET_REVOC_REG_DEF:
        return domain.prepare_revoc_def_for_state(result['data'])
    if request_type == GET_REVOC_REG:
        return domain.prepare_revoc_reg_entry_accum_for_state(result['data'])
    if request_type == GET_REVOC_REG_DELTA:
        if ISSUED in result['data'][VALUE]:
            return domain.prepare_revoc_reg_entry_for_state(result['data'])
        else:
            return domain.prepare_revoc_reg_entry_accum_for_state(result['data'])
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
            reply_from = {DATA: result['data'][VALUE][ACCUM_FROM],
                          STATE_PROOF: result['data'][STATE_PROOF_FROM],
                          TYPE: result[TYPE]}
            assert validate_proof(reply_from)
        reply_to = {DATA: result['data'][VALUE][ACCUM_TO],
                    STATE_PROOF: result[STATE_PROOF],
                    TYPE: result[TYPE]}
        assert validate_proof(reply_to)
    else:
        assert validate_proof(result)
